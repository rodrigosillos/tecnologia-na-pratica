using System;
using System.IO;
using NUnit.Framework;
using TecnologiaNaPratica;
public class PlataformaTests
{
    string pasta,arquivo;
    [SetUp]public void Inicio(){pasta=Path.Combine(Path.GetTempPath(),"TNP-Teste-"+Guid.NewGuid());arquivo=Path.Combine(pasta,"save.json");}
    [TearDown]public void Fim(){if(Directory.Exists(pasta))Directory.Delete(pasta,true);}
    [Test]public void PuloAposBordaDentroDaJanela(){var s=new JanelaSalto();s.RegistrarSolo(1);s.Pedir(1.08f);Assert.IsTrue(s.Consumir(1.08f));Assert.IsFalse(s.Consumir(1.09f));}
    [Test]public void PuloMuitoTardeNaoFunciona(){var s=new JanelaSalto();s.RegistrarSolo(1);s.Pedir(1.2f);Assert.IsFalse(s.Consumir(1.2f));}
    [Test]public void BufferAntesDeAterrissar(){var s=new JanelaSalto();s.Pedir(1);s.RegistrarSolo(1.08f);Assert.IsTrue(s.Consumir(1.08f));}
    [Test]public void BufferExpiradoNaoSalta(){var s=new JanelaSalto();s.Pedir(1);s.RegistrarSolo(1.2f);Assert.IsFalse(s.Consumir(1.2f));}
    [Test]public void ReinicioApagaIntencao(){var s=new JanelaSalto();s.Pedir(1);s.RegistrarSolo(1);s.Limpar();Assert.IsFalse(s.Consumir(1));}
    [Test]public void ArquivoAusenteRetornaNulo(){Assert.IsNull(new RepositorioProgresso(arquivo).Carregar());}
    [Test]public void SalvarReabrirPreservaDados(){var r=new RepositorioProgresso(arquivo);var d=new DadosProgresso{fase=1,checkpoint=2,mortes=4};d.Coletar(5);Assert.IsTrue(r.Salvar(d));var l=r.Carregar();Assert.AreEqual(1,l.fase);Assert.AreEqual(2,l.checkpoint);Assert.IsTrue(l.Coletado(5));}
    [Test]public void CristalNaoContaDuasVezes(){var d=new DadosProgresso();d.Coletar(3);d.Coletar(3);Assert.AreEqual(1,d.Total);d.fase=1;d.Coletar(3);Assert.AreEqual(2,d.Total);}
    [Test]public void PrincipalCorrompidaUsaBackup(){var r=new RepositorioProgresso(arquivo);r.Salvar(new DadosProgresso{checkpoint=1});r.Salvar(new DadosProgresso{checkpoint=2});File.WriteAllText(arquivo,"quebrado");Assert.AreEqual(1,r.Carregar().checkpoint);StringAssert.Contains("recuperado",r.Aviso);}
    [Test]public void VersaoFuturaNaoEInterpretada(){Directory.CreateDirectory(pasta);File.WriteAllText(arquivo,"{\"versao\":99,\"fase\":0,\"checkpoint\":0,\"cristais\":[0,0,0]}");Assert.IsNull(new RepositorioProgresso(arquivo).Carregar());}
    [Test]public void DadosForaDoContratoNaoSalvam(){var r=new RepositorioProgresso(arquivo);Assert.IsFalse(r.Salvar(new DadosProgresso{fase=8}));Assert.IsFalse(File.Exists(arquivo));}
    [Test]public void RecuperacaoNaoDestruiBackupBom(){var r=new RepositorioProgresso(arquivo);r.Salvar(new DadosProgresso{checkpoint=1});r.Salvar(new DadosProgresso{checkpoint=2});File.WriteAllText(arquivo,"invalido");var d=r.Carregar();Assert.IsTrue(r.Salvar(d));File.WriteAllText(arquivo,"invalido outra vez");Assert.AreEqual(1,r.Carregar().checkpoint);}
}
