using System;
using System.Windows.Forms;

namespace NetAcceleratorWin
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            // 启动伪装加速器界面
            Application.Run(new SplashForm());
        }
    }
}