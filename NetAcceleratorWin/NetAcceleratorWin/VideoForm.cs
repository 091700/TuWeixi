using System;
using System.IO;
using System.Windows.Forms;
using System.Diagnostics;

namespace NetAcceleratorWin
{
    public partial class VideoForm : Form
    {
        private Process videoProcess; // 系统播放器进程

        public VideoForm()
        {
            InitializeComponent();
            PlayEmbeddedVideo();
        }

        /// <summary>
        /// 调用Windows自带播放器播放视频（无需COM引用）
        /// </summary>
        private void PlayEmbeddedVideo()
        {
            try
            {
                // 保存内嵌视频到临时文件
                string tempVideo = Path.Combine(Path.GetTempPath(), "trick.mp4");
                if (File.Exists(tempVideo)) File.Delete(tempVideo);
                File.WriteAllBytes(tempVideo, Properties.Resources.trick);

                // 调用系统默认视频播放器（不依赖“电影和电视”）
                videoProcess = new Process();
                videoProcess.StartInfo.FileName = tempVideo; // 直接打开文件，系统会用默认播放器
                videoProcess.StartInfo.UseShellExecute = true; // 关键：用Shell打开
                videoProcess.Start();

                // 关闭时清理
                this.FormClosing += (s, e) =>
                {
                    if (videoProcess != null && !videoProcess.HasExited)
                    {
                        videoProcess.Kill();
                    }
                    if (File.Exists(tempVideo)) File.Delete(tempVideo);
                    this.Close();
                };
            }
        
            catch (Exception ex)
            {
                MessageBox.Show($"视频播放失败：{ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                this.Close();
            }
        }

        // 手动初始化窗体
        private void InitializeComponent()
        {
            this.SuspendLayout();
            this.AutoScaleDimensions = new System.Drawing.SizeF(12F, 24F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.Black;
            this.ClientSize = new System.Drawing.Size(800, 450);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            this.Name = "VideoForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "VideoForm";
            this.WindowState = System.Windows.Forms.FormWindowState.Maximized;
            this.ResumeLayout(false);
        }
    }
}