using System.ServiceProcess;

namespace DrFujiBot_Twitch
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        static void Main()
        {
            ServiceBase[] ServicesToRun;
            ServicesToRun = new ServiceBase[]
            {
                new TwitchService()
            };
            ServiceBase.Run(ServicesToRun);
        }
    }
}
