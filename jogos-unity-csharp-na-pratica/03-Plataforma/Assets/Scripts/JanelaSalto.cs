namespace TecnologiaNaPratica
{
    public sealed class JanelaSalto
    {
        float coyoteAte = -1, bufferAte = -1;
        public void RegistrarSolo(float agora)
        {
            coyoteAte = agora + .12f;
        }

        public void Pedir(float agora)
        {
            bufferAte = agora + .12f;
        }

        public bool Consumir(float agora)
        {
            if (agora > coyoteAte || agora > bufferAte)
                return false;
            coyoteAte = bufferAte = -1;
            return true;
        }

        public void Limpar()
        {
            coyoteAte = bufferAte = -1;
        }
    }
}
