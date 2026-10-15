import http.client
import json
import threading
import unittest
from adapters import StubGenerator
from bootstrap import wire
from http_api import make_server


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.service=wire()
        self.server=make_server(self.service)
        self.thread=threading.Thread(target=self.server.serve_forever,
                                     kwargs={'poll_interval':.01},daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.assertFalse(self.thread.is_alive())

    def call(self,body=None,token='acme-demo',path='/v1/answers',method='POST',ctype='application/json'):
        if body is None:body=b'{"topic":"returns","language":"pt-BR"}'
        if isinstance(body,dict):body=json.dumps(body).encode('utf-8')
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        headers={'Content-Type':ctype}
        if token is not None:headers['Authorization']='Bearer '+token
        try:
            c.request(method,path,body,headers)
            r=c.getresponse()
            return r.status,json.loads(r.read()),dict(r.getheaders())
        finally:c.close()

    def test_real_http_answer_and_correlation(self):
        status,r,h=self.call()
        self.assertEqual(status,200)
        self.assertEqual(r['citation'],'acme-returns-v2')
        self.assertEqual(r['request_id'],h['X-Request-ID'])
        self.assertEqual(h['Cache-Control'],'no-store')

    def test_identity_cannot_be_selected_by_body(self):
        status,r,_=self.call({'topic':'refund','language':'en-US','tenant':'zen'})
        self.assertEqual((status,r['reason']),(400,'invalid_request'))

    def test_unknown_and_absent_identity(self):
        for token in ('unknown',None):
            status,r,h=self.call(token=token)
            self.assertEqual(status,401)
            self.assertIn('WWW-Authenticate',h)

    def test_two_tenants_over_http(self):
        body={'topic':'refund','language':'en-US'}
        a=self.call(body)[1];z=self.call(body,token='zen-demo')[1]
        self.assertEqual(a['citation'],'acme-refund-v1')
        self.assertEqual(z['citation'],'zen-refund-v1')

    def test_abstention_is_http200_but_not_answer(self):
        status,r,_=self.call({'topic':'sunday','language':'pt-BR'})
        self.assertEqual((status,r['status']),(200,'abstain'))
        self.assertIsNone(r['answer'])

    def test_malformed_and_duplicate_json(self):
        for body in (b'{',b'[]',b'{"topic":"returns","topic":"refund","language":"pt-BR"}'):
            self.assertEqual(self.call(body)[0],400)

    def test_invalid_language_is_client_error(self):
        self.assertEqual(self.call({'topic':'returns','language':'fr'})[0],400)

    def test_size_and_content_type(self):
        self.assertEqual(self.call(b'x'*2049)[0],413)
        self.assertEqual(self.call(ctype='text/plain')[0],415)

    def test_paths_and_method(self):
        self.assertEqual(self.call(path='/other')[0],404)
        status,_,h=self.call(method='GET')
        self.assertEqual(status,405)
        self.assertEqual(h['Allow'],'POST')

    def test_health_does_not_call_generator(self):
        self.service.generator=StubGenerator('unexpected')
        status,r,_=self.call(path='/health',method='GET')
        self.assertEqual((status,r['status']),(200,'ok'))

    def test_dependency_mapping(self):
        for mode,status in [('malformed',502),('timeout',504),('unavailable',503),
                            ('incomplete',502),('refused',502),('expensive',503)]:
            self.service.generator=StubGenerator(mode)
            observed,r,_=self.call()
            self.assertEqual(observed,status)
            self.assertEqual(r['status'],'error')

    def test_unexpected_error_redacted(self):
        self.service.generator=StubGenerator('unexpected')
        status,r,_=self.call()
        self.assertEqual((status,r['reason']),(500,'internal_error'))
        self.assertNotIn('private',json.dumps(r))


if __name__=='__main__':unittest.main()
