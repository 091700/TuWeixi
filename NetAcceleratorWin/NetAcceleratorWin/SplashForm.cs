using System;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace NetAcceleratorWin
{
    public partial class SplashForm : Form
    {
        public SplashForm()
        {
            InitializeComponent(); // 这行必须保留，关联Designer
        }

        // 按钮点击事件（异步延迟，不卡界面）
        private async void btnEnter_Click(object sender, EventArgs e)
        {
            await Task.Delay(500);
            VideoForm videoForm = new VideoForm();
            videoForm.Show();
            this.Hide();
        }
    }
}