#!/usr/bin/env python3
"""安全 OSS 上传服务 — 在本地监听，接收密钥后自动上传，用完即删"""
import http.server
import json
import subprocess
import os
import sys
import tempfile

PORT = 18888
SOURCE_DIR = os.path.expanduser("~/.openclaw/workspace/idle_platform")
OSSUTIL = "/tmp/ossutil-v1.7.18-linux-amd64/ossutil64"
BUCKET = "chenghelck"
ENDPOINT = "oss-cn-beijing.aliyuncs.com"

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/oss_config.html":
            with open(os.path.join(SOURCE_DIR, "oss_config.html"), "r") as f:
                html = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/upload":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            ak_id = data.get("accessKeyId", "").strip()
            ak_secret = data.get("accessKeySecret", "").strip()

            if not ak_id or not ak_secret:
                self._json({"ok": False, "message": "❌ 请填写完整的 AccessKey ID 和 Secret"})
                return

            # 创建临时配置
            cfg = tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False, prefix="oss_")
            cfg.write(f"[Credentials]\nlanguage=CH\nendpoint={ENDPOINT}\naccessKeyID={ak_id}\naccessKeySecret={ak_secret}\n")
            cfg.close()

            try:
                result = subprocess.run(
                    [OSSUTIL, "cp", "-r", "-f", "--config-file", cfg.name,
                     SOURCE_DIR + "/", f"oss://{BUCKET}/huaijiu-zahuopu/"],
                    capture_output=True, text=True, timeout=120
                )
                if result.returncode == 0:
                    url = f"https://{BUCKET}.{ENDPOINT}/huaijiu-zahuopu/index.html"
                    self._json({"ok": True, "message": f"✅ 上传成功！访问: {url}"})
                else:
                    err = result.stderr.strip() or result.stdout.strip()
                    self._json({"ok": False, "message": f"❌ 上传失败: {err[:200]}"})
            except Exception as e:
                self._json({"ok": False, "message": f"❌ 错误: {str(e)[:200]}"})
            finally:
                os.unlink(cfg.name)  # 立刻删除，不留痕迹
        else:
            self.send_response(404)
            self.end_headers()

    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        pass  # 不打印日志

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"服务已启动 → http://127.0.0.1:{PORT}")
    print("在浏览器打开后填写密钥，自动上传，密钥用完即删。")
    sys.stdout.flush()
    server.serve_forever()
