using System;
using System.IO;
using UnityEngine;

namespace TecnologiaNaPratica
{
    [Serializable]
    public sealed class DadosProgresso
    {
        public int versao = 1, fase, checkpoint, mortes;
        public int[] cristais = new int[3];
        public bool concluido;
        public bool Valido() => versao == 1 && fase >= 0 && fase < 3 && checkpoint >= 0 && checkpoint <= 2 && mortes >= 0 && cristais != null && cristais.Length == 3 && Array.TrueForAll(cristais, x => x >= 0 && x < (1 << 24));
        public bool Coletado(int id) => (cristais[fase] & (1 << id)) != 0;
        public void Coletar(int id)
        {
            if (id >= 0 && id < 24)
                cristais[fase] |= 1 << id;
        }

        public int Total
        {
            get
            {
                int n = 0;
                foreach (int conjunto in cristais)
                    for (int b = 0; b < 24; b++)
                        if ((conjunto & (1 << b)) != 0)
                            n++;
                return n;
            }
        }
    }

    public sealed class RepositorioProgresso
    {
        readonly string caminho;
        public string Aviso { get; private set; } = "";

        public RepositorioProgresso(string arquivo)
        {
            caminho = arquivo;
        }

        DadosProgresso Ler(string path)
        {
            if (!File.Exists(path) || new FileInfo(path).Length > 65536)
                return null;
            try
            {
                var d = JsonUtility.FromJson<DadosProgresso>(File.ReadAllText(path));
                return d != null && d.Valido() ? d : null;
            }
            catch (ArgumentException)
            {
                return null;
            }
            catch (IOException)
            {
                return null;
            }
            catch (UnauthorizedAccessException)
            {
                return null;
            }
        }

        public DadosProgresso Carregar()
        {
            Aviso = "";
            var d = Ler(caminho);
            if (d != null)
                return d;
            d = Ler(caminho + ".bak");
            if (d != null)
                Aviso = "Progresso recuperado da cópia de segurança.";
            else if (File.Exists(caminho))
                Aviso = "O progresso não pôde ser lido. Uma nova partida está disponível.";
            return d;
        }

        public bool Salvar(DadosProgresso dados)
        {
            if (dados == null || !dados.Valido())
                return false;
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(caminho));
                string temporario = caminho + ".tmp";
                File.WriteAllText(temporario, JsonUtility.ToJson(dados, true));
                // Preserva a última versão válida; uma principal corrompida não deve substituir o backup bom.
                if (File.Exists(caminho) && Ler(caminho) != null)
                    File.Replace(temporario, caminho, caminho + ".bak");
                else
                {
                    if (File.Exists(caminho))
                        File.Delete(caminho);
                    File.Move(temporario, caminho);
                }

                Aviso = "";
                return true;
            }
            catch (IOException)
            {
                Aviso = "Não foi possível salvar. A sessão continua na memória.";
                return false;
            }
            catch (UnauthorizedAccessException)
            {
                Aviso = "Sem acesso à pasta de progresso. A sessão continua na memória.";
                return false;
            }
        }
    }
}
