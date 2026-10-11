using System.Collections.Generic;
using UnityEngine;

namespace TecnologiaNaPratica.QuebraBlocos
{
    [RequireComponent(typeof(AudioSource))]
    public sealed class SomJogo : MonoBehaviour
    {
        AudioSource fonte;
        readonly Dictionary<int, AudioClip> tons = new Dictionary<int, AudioClip>();
        public float Volume { get; private set; }
        const string ChaveVolume = "TNP.QuebraBlocos.Volume.v1";
        void Awake()
        {
            fonte = GetComponent<AudioSource>();
            fonte.playOnAwake = false;
            Volume = Mathf.Clamp01(PlayerPrefs.GetFloat(ChaveVolume, 0.45f));
            fonte.volume = Volume;
        }
        public void DefinirVolume(float valor)
        {
            Volume = Mathf.Clamp01(valor);
            fonte.volume = Volume;
            PlayerPrefs.SetFloat(ChaveVolume, Volume);
        }
        public void Toque(int frequencia, float duracao)
        {
            if (!tons.TryGetValue(frequencia, out var clip))
            {
                const int taxa = 22050;
                int tamanho = Mathf.CeilToInt(taxa * duracao);
                var dados = new float[tamanho];
                for (int i = 0; i < tamanho; i++)
                {
                    float envelope = Mathf.Sin(Mathf.PI * i / tamanho);
                    dados[i] = Mathf.Sin(2f * Mathf.PI * frequencia * i / taxa) * envelope * 0.22f;
                }
                clip = AudioClip.Create("Tom " + frequencia, tamanho, 1, taxa, false);
                clip.SetData(dados, 0);
                tons.Add(frequencia, clip);
            }
            fonte.PlayOneShot(clip);
        }
        void OnDestroy() { foreach (var clip in tons.Values) Destroy(clip); }
        void OnApplicationQuit() { PlayerPrefs.Save(); }
    }
}
