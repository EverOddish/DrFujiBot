using System.ServiceProcess;
using System;
using TwitchLib.Client;
using TwitchLib.Client.Events;
using TwitchLib.Client.Models;
using TwitchLib.Communication.Clients;
using TwitchLib.Communication.Models;
using System.IO;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Net;
using System.Timers;
using System.Linq;

namespace DrFujiBot_Twitch
{
    public partial class TwitchService : ServiceBase
    {
        TwitchClient client;
        Timer timer;
        Dictionary<string, string> config;
        System.Diagnostics.EventLog eventLog;
        const string serviceName = "DrFujiBot Twitch Service";

        public TwitchService()
        {
            InitializeComponent();

            eventLog = new System.Diagnostics.EventLog();
            if (!System.Diagnostics.EventLog.SourceExists(serviceName))
            {
                System.Diagnostics.EventLog.CreateEventSource(serviceName, serviceName);
            }
            eventLog.Source = serviceName;
            eventLog.Log = "";

            client = null;

            CanHandlePowerEvent = true;
        }

        private void startBot()
        {
            string configFilePath = System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "config.json");
            using (StreamReader r = new StreamReader(configFilePath))
            {
                string json = r.ReadToEnd();
                config = JsonConvert.DeserializeObject<Dictionary<string, string>>(json);
            }

            // The purpose of scrambling the token is mainly to prevent bots from scraping the token from GitHub.
            // Please do not use this token for any other purpose than the normal functions of DrFujiBot. Thank you.
            ConnectionCredentials credentials = new ConnectionCredentials("DrFujiBot", getToken());
            var clientOptions = new ClientOptions
            {
                MessagesAllowedInPeriod = 750,
                ThrottlingPeriod = TimeSpan.FromSeconds(30)
            };
            TcpClient customClient = new TcpClient(clientOptions);
            client = new TwitchClient(customClient);
            client.Initialize(credentials, config["twitch_channel"]);

            client.OnMessageReceived += Client_OnMessageReceived;
            client.OnIncorrectLogin += Client_OnIncorrectLogin;
            client.OnConnectionError += Client_OnConnectionError;

            client.Connect();

            timer = new Timer();
            timer.Interval = 30000; // 30 seconds
            timer.Elapsed += new ElapsedEventHandler(this.OnTimer);
            timer.Start();
        }

        private void stopBot()
        {
            if (null != client)
            {
                client.Disconnect();
                client = null;
            }

            if (null != timer)
            {
                timer.Stop();
                timer = null;
            }
        }

        protected override void OnStart(string[] args)
        {
            startBot();
        }

        protected override void OnStop()
        {
            stopBot();
        }

        protected override bool OnPowerEvent(PowerBroadcastStatus powerStatus)
        {
            if (powerStatus.HasFlag(PowerBroadcastStatus.QuerySuspend))
            {
                stopBot();
            }

            if (powerStatus.HasFlag(PowerBroadcastStatus.ResumeSuspend))
            {
                startBot();
            }

            return base.OnPowerEvent(powerStatus);
        }

        private string unscrambleToken(string scrambledToken)
        {
            string unscrambledToken = "";

            for(int i = 0; i < 30; i += 2)
            {
                unscrambledToken += scrambledToken[i];
            }

            for(int i = 1; i < 30; i += 2)
            {
                unscrambledToken += scrambledToken[i];
            }

            return unscrambledToken;
        }

        private string getToken()
        {
            string token = "";

            try
            {
                string url = "https://raw.githubusercontent.com/EverOddish/DrFujiBot/master/DrFujiBot_Django/data/access_token.txt";
                WebRequest request = WebRequest.Create(url);
                Stream objStream = request.GetResponse().GetResponseStream();
                StreamReader objReader = new StreamReader(objStream);
                string line =  objReader.ReadToEnd();

                if (null != line && line.Length > 0)
                {
                    token = unscrambleToken(line);
                }
            }
            catch (Exception e)
            {
                eventLog.WriteEntry(e.ToString());
            }

            return token;
        }

        private void requestAndDisplay(string url)
        {
            try
            {
                WebRequest request = WebRequest.Create(url);
                Stream objStream = request.GetResponse().GetResponseStream();
                StreamReader objReader = new StreamReader(objStream);
                string line = "";

                while (line != null)
                {
                    line = objReader.ReadLine();

                    if (null != line && line.Length > 0 && !line.Contains("<!DOCTYPE html>"))
                    {
                        outputMessage(line);
                    }
                }
            }
            catch (Exception e)
            {
                eventLog.WriteEntry(e.ToString());
            }
        }

        private IEnumerable<string> split(string str, int chunkSize)
        {
            if (str.Length <= chunkSize)
            {
                return new List<string>() { str };
            }
            else
            {
                return Enumerable.Range(0, str.Length / chunkSize).Select(i => str.Substring(i * chunkSize, chunkSize));
            }
        }

        private void outputMessage(string message)
        {
            const int maxMessageSize = 480;
            int chunkSize = maxMessageSize - 10;

            if (client != null)
            {
                var chunks = split(message, chunkSize);
                string line = "";
                int i = 1;

                foreach (var chunk in chunks)
                {
                    eventLog.WriteEntry(chunk);
                    if (chunks.Count() > 1)
                    {
                        line = "(" + i + "/" + chunks.Count() + ") " + chunk;
                    }
                    else
                    {
                        line = chunk;
                    }

                    client.SendMessage(config["twitch_channel"], line);
                    i++;
                }
            }
        }

        private void Client_OnMessageReceived(object sender, OnMessageReceivedArgs e)
        {
            string url = "http://127.0.0.1:41945/dashboard/drfujibot/?";

            url += "is_broadcaster=" + (e.ChatMessage.IsBroadcaster ? "True" : "False") + "&";
            url += "is_moderator=" + (e.ChatMessage.IsModerator ? "True" : "False") + "&";
            url += "is_subscriber=" + (e.ChatMessage.IsSubscriber ? "True" : "False") + "&";
            url += "username=" + e.ChatMessage.Username + "&";
            url += "line=" + e.ChatMessage.Message;

            requestAndDisplay(url);
        }

        private void Client_OnIncorrectLogin(object sender, OnIncorrectLoginArgs e)
        {
            eventLog.WriteEntry("Incorrect login: " + e.Exception.ToString());
        }

        private void Client_OnConnectionError(object sender, OnConnectionErrorArgs e)
        {
            eventLog.WriteEntry("Connection error: " + e.Error.ToString());
        }

        public void OnTimer(object sender, ElapsedEventArgs args)
        {
            string url = "http://127.0.0.1:41945/dashboard/timed_messages/";

            requestAndDisplay(url);
        }
    }
}
