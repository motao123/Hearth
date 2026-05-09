#!/bin/bash
# Hearth 一键部署脚本（Docker + 宝塔 Nginx 反代）
# 用法: bash deploy.sh
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ---- 检查 Docker ----
if ! command -v docker &>/dev/null; then
    error "Docker 未安装。请先在宝塔软件商店安装 Docker 管理器"
fi
if ! docker compose version &>/dev/null; then
    error "Docker Compose 未安装。请先在宝塔 Docker 管理器中安装"
fi

# ---- 收集配置 ----
echo ""
echo "========================================="
echo "   Hearth 家庭管理平台 — 一键部署"
echo "========================================="
echo ""

# 域名
read -p "请输入你的域名（如 hearth.example.com）: " DOMAIN
if [ -z "$DOMAIN" ]; then
    error "域名不能为空"
fi

# 生成密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -hex 32)
info "已自动生成 JWT 密钥"

# ---- 写入 .env ----
cat > .env << EOF
# Hearth 生产环境配置
HEARTH_SECRET_KEY=${SECRET_KEY}
HEARTH_SESSION_EXPIRE_HOURS=72
HEARTH_DEBUG=false
HEARTH_CORS_ORIGINS=https://${DOMAIN}
HEARTH_DB_PATH=data/hearth.db
HEARTH_UPLOAD_DIR=data/uploads
HEARTH_BACKUP_DIR=backups
HEARTH_BACKUP_CRON=0 3 * * *
HEARTH_BACKUP_RETENTION=7
HEARTH_UPLOAD_MAX_SIZE_MB=10
HEARTH_RATE_LIMIT_ENABLED=true
HEARTH_RATE_LIMIT_LOGIN=5/minute
HEARTH_RATE_LIMIT_REGISTER=3/minute
EOF

info ".env 配置已生成"
warn "JWT 密钥已写入 .env，请妥善保管此文件"

# ---- 启动 Docker ----
info "正在构建并启动 Docker 容器（首次可能需要几分钟）..."
docker compose up -d --build

info "等待服务启动..."
sleep 5

# 健康检查
if curl -sf http://127.0.0.1:8090/api/health >/dev/null 2>&1; then
    info "后端服务启动成功 ✓"
else
    warn "后端服务可能还在启动中，请稍后检查: docker compose logs"
fi

# ---- Nginx 反代配置 ----
echo ""
echo "========================================="
echo "   Nginx 配置（需在宝塔面板操作）"
echo "========================================="
echo ""
echo "1. 宝塔 → 网站 → 添加站点"
echo "   域名: ${DOMAIN}"
echo "   根目录: 随意（用不到）"
echo ""
echo "2. 站点设置 → SSL → Let's Encrypt → 申请证书"
echo ""
echo "3. 站点设置 → 配置文件 → 粘贴以下内容:"
echo ""

cat << NGINX
server {
    listen 80;
    server_name ${DOMAIN};
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate    /www/server/panel/vhost/cert/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /www/server/panel/vhost/cert/${DOMAIN}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    client_max_body_size 10m;

    location / {
        proxy_pass http://127.0.0.1:8090;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location ~ /\. {
        deny all;
    }

    access_log /www/wwwlogs/hearth.log;
    error_log /www/wwwlogs/hearth.error.log;
}
NGINX

echo ""
echo "========================================="
echo "   部署完成！"
echo "========================================="
echo ""
echo "访问地址: https://${DOMAIN}"
echo ""
echo "常用命令:"
echo "  查看日志:   docker compose logs -f"
echo "  重启服务:   docker compose restart"
echo "  停止服务:   docker compose down"
echo "  更新代码:   git pull && docker compose up -d --build"
echo ""
