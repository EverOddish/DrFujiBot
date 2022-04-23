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
        Timer message_timer;
        Timer reload_timer;
        Dictionary<string, string> config;
        System.Diagnostics.EventLog eventLog;
        const string serviceName = "DrFujiBot Twitch Service";
        bool running;
        private object lockObject;

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
            running = false;
            lockObject = new object();
        }

        private void startBot()
        {
            lock (lockObject)
            {
                if (!running)
                {
                    string configFilePath = System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "config.json");
                    using (StreamReader r = new StreamReader(configFilePath))
                    {
                        string json = r.ReadToEnd();
                        config = JsonConvert.DeserializeObject<Dictionary<string, string>>(json);
                    }

                    ConnectionCredentials credentials = new ConnectionCredentials("DrFujiBot", config["twitch_oauth_token"]);
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

                    message_timer = new Timer();
                    message_timer.Interval = 30000; // 30 seconds
                    message_timer.Elapsed += new ElapsedEventHandler(this.OnMessageTimer);
                    message_timer.Start();

                    reload_timer = new Timer();
                    reload_timer.Interval = 3000; // 3 seconds
                    reload_timer.Elapsed += new ElapsedEventHandler(this.OnReloadTimer);
                    reload_timer.Start();

                    running = true;
                }
            }
        }

        private void stopBot()
        {
            lock (lockObject)
            {
                if (running)
                {
                    if (null != client)
                    {
                        client.Disconnect();
                        client = null;
                    }

                    if (null != message_timer)
                    {
                        message_timer.Stop();
                        message_timer = null;
                    }

                    if (null != reload_timer)
                    {
                        reload_timer.Stop();
                        reload_timer = null;
                    }

                    running = false;
                }
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
            if (PowerBroadcastStatus.QuerySuspend == powerStatus ||
                PowerBroadcastStatus.Suspend == powerStatus )
            {
                eventLog.WriteEntry("Stopping DrFujiBot Twitch IRC due to system suspend");
                stopBot();
            }

            if (PowerBroadcastStatus.ResumeSuspend == powerStatus ||
                PowerBroadcastStatus.ResumeAutomatic == powerStatus)
            {
                eventLog.WriteEntry("Starting DrFujiBot Twitch IRC due to system resume");
                startBot();
            }

            return base.OnPowerEvent(powerStatus);
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
                    //eventLog.WriteEntry(chunk);

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

        public void OnMessageTimer(object sender, ElapsedEventArgs args)
        {
            string url = "http://127.0.0.1:41945/dashboard/timed_messages/";

            requestAndDisplay(url);
        }
        public void OnReloadTimer(object sender, ElapsedEventArgs args)
        {
            string reloadFilePath = System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "reload.txt");

            if (File.Exists(reloadFilePath)) {
                eventLog.WriteEntry("Reload file found, restarting bot.");
                File.Delete(reloadFilePath);
                stopBot();
                startBot();
            }
        }
    }
}
