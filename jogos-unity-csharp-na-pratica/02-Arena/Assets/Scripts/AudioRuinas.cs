using System.Collections.Generic;
using UnityEngine;

namespace TecnologiaNaPratica
{
    public sealed class AudioRuinas : MonoBehaviour
    {
        AudioSource efeitos, musica;
        readonly Dictionary<int, AudioClip> tons = new Dictionary<int, AudioClip>();
        string chave;
        public float Efeitos { get; private set; }
        public float Musica { get; private set; }

        public void Preparar(string produto)
        {
            chave = "TNP." + produto;
            efeitos = gameObject.AddComponent<AudioSource>();
            musica = gameObject.AddComponent<AudioSource>();
            Efeitos = PlayerPrefs.GetFloat(chave + ".fx", .45f);
            Musica = PlayerPrefs.GetFloat(chave + ".musica", .18f);
            efeitos.volume = Efeitos;
            musica.volume = Musica;
            const int taxa = 22050;
            var dados = new float[taxa * 8];
            int[] notas =
            {
                220,
                262,
                330,
                294,
                220,
                196,
                262,
                294
            };
            for (int i = 0; i < dados.Length; i++)
            {
                float t = (i % taxa) / (float)taxa;
                dados[i] = Mathf.Sin(i * 2 * Mathf.PI * notas[i / taxa] / taxa) * Mathf.Sin(Mathf.PI * t) * .10f;
            }

            var clip = AudioClip.Create("Tema original das ruinas", dados.Length, 1, taxa, false);
            clip.SetData(dados, 0);
            musica.clip = clip;
            musica.loop = true;
            musica.Play();
        }

        public void DefinirEfeitos(float v)
        {
            Efeitos = Mathf.Clamp01(v);
            efeitos.volume = Efeitos;
            PlayerPrefs.SetFloat(chave + ".fx", Efeitos);
        }

        public void DefinirMusica(float v)
        {
            Musica = Mathf.Clamp01(v);
            musica.volume = Musica;
            PlayerPrefs.SetFloat(chave + ".musica", Musica);
        }

        public void Tocar(int hz)
        {
            if (!tons.TryGetValue(hz, out var clip))
            {
                const int taxa = 22050;
                var d = new float[2205];
                for (int i = 0; i < d.Length; i++)
                    d[i] = Mathf.Sin(2 * Mathf.PI * hz * i / taxa) * (.22f * (1 - i / (float)d.Length));
                clip = AudioClip.Create("Tom " + hz, d.Length, 1, taxa, false);
                clip.SetData(d, 0);
                tons.Add(hz, clip);
            }

            efeitos.PlayOneShot(clip);
        }

        void OnDestroy()
        {
            foreach (var c in tons.Values)
                Destroy(c);
            if (musica)
                Destroy(musica.clip);
            PlayerPrefs.Save();
        }
    }
}
