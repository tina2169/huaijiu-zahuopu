#!/bin/bash
# ============================================================
#  怀旧杂货铺 → 阿里云 OSS 一键上传脚本
#  使用方式: bash upload_to_oss.sh
#  密钥仅在终端交互式输入，不会出现在日志或历史中
# ============================================================

BUCKET="chenghelck"
ENDPOINT="oss-cn-beijing.aliyuncs.com"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
REMOTE_DIR="huaijiu-zahuopu/"

echo "============================================================"
echo " ♻️  怀旧杂货铺 → 阿里云 OSS 上传工具"
echo "============================================================"
echo ""
echo "  存储空间: $BUCKET"
echo "  Endpoint: $ENDPOINT"
echo "  本地目录: $SOURCE_DIR"
echo "  远程路径: $REMOTE_DIR"
echo ""

# 安全读取（不回显密码）
read -r -p " 请输入 AccessKey ID: "  ACCESS_KEY_ID
read -r -s -p " 请输入 AccessKey Secret: " ACCESS_KEY_SECRET
echo ""  # 换行

# 生成临时 ossutil 配置（用完即删）
OSSUTIL_CONFIG=$(mktemp)
trap "rm -f $OSSUTIL_CONFIG" EXIT

cat > "$OSSUTIL_CONFIG" <<EOF
[Credentials]
language=CH
endpoint=$ENDPOINT
accessKeyID=$ACCESS_KEY_ID
accessKeySecret=$ACCESS_KEY_SECRET
EOF

# 下载 ossutil（如果不存在）
OSSUTIL_BIN="/tmp/ossutil-v1.7.18-linux-amd64/ossutil64"
if [ ! -x "$OSSUTIL_BIN" ]; then
    echo ""
    echo "📦 正在下载 ossutil..."
    mkdir -p /tmp/ossutil-install
    cd /tmp/ossutil-install
    curl -sSL https://gosspublic.alicdn.com/ossutil/1.7.18/ossutil-v1.7.18-linux-amd64.zip -o ossutil.zip
    unzip -oq ossutil.zip
    OSSUTIL_BIN="/tmp/ossutil-install/ossutil-v1.7.18-linux-amd64/ossutil64"
    chmod +x "$OSSUTIL_BIN"
fi

echo ""
echo "🚀 开始上传..."
echo "------------------------------------------------------------"

# 上传整个文件夹（递归、覆盖、显示进度）
"$OSSUTIL_BIN" cp -r -f \
    --config-file "$OSSUTIL_CONFIG" \
    "$SOURCE_DIR/" \
    "oss://$BUCKET/$REMOTE_DIR"

EXIT_CODE=$?
echo "------------------------------------------------------------"

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ 上传成功！"
    echo ""
    echo "  访问地址示例:"
    echo "  https://$BUCKET.$ENDPOINT/${REMOTE_DIR}index.html"
    echo ""
else
    echo ""
    echo "❌ 上传失败，请检查 AccessKey 或网络设置。"
    echo ""
fi

# 密钥已随 trap 自动清理
exit $EXIT_CODE
