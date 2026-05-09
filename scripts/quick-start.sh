#!/bin/bash
# Hearth 快速启动脚本 — 无需 git clone，直接拉取镜像部署
# 用法: bash <(curl -s https://raw.githubusercontent.com/motao123/Hearth/main/scripts/quick-start.sh)
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo ""
echo "========================================="
echo "   Hearth 家庭管理平台 — 快速启动"
echo "========================================="
echo ""

# ---- 检查 Docker ----
if ! command -v docker &>/dev/null; then
    error "Docker 未安装，请先安装: https://docs.docker.com/get-docker/"
fi
if ! docker compose version &>/dev/null; then
    error "Docker Compose 未安装"
fi

# ---- 创建工作目录 ----
INSTALL_DIR="${1:-/opt/hearth}"
info "安装目录: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# ---- 收集配置 ----
read -p "请输入你的域名（如 hearth.example.com，无域名可直接回车跳过）: " DOMAIN

# 生成密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -hex 32)
info "已自动生成 JWT 密钥"

if [ -n "$DOMAIN" ]; then
    CORS="https://${DOMAIN}"
else
    CORS="http://$(hostname -I 2>/dev/null | awk '{print $1}' || echo 'localhost'):8090"
    warn "未设置域名，CORS 设为 $CORS"
fi

# ---- 写入 .env ----
cat > .env << EOF
# Hearth 生产环境配置
HEARTH_SECRET_KEY=${SECRET_KEY}
HEARTH_SESSION_EXPIRE_HOURS=72
HEARTH_DEBUG=false
HEARTH_CORS_ORIGINS=${CORS}
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

info ".env 已生成"

# ---- 写入 docker-compose.yml ----
cat > docker-compose.yml << 'COMPOSE'
services:
  hearth:
    image: imotao/hearth:latest
    container_name: hearth
    ports:
      - "127.0.0.1:8090:8090"
    volumes:
      - hearth-data:/app/data
      - hearth-backups:/app/backups
    env_file: .env
    restart: unless-stopped

volumes:
  hearth-data:
  hearth-backups:
COMPOSE

# ---- 拉取镜像并启动 ----
info "正在拉取 Docker 镜像（首次可能需要几分钟）..."
docker compose pull
docker compose up -d

info "等待服务启动..."
sleep 5

# 健康检查
if curl -sf http://127.0.0.1:8090/api/health >/dev/null 2>&1; then
    info "服务启动成功 ✓"
else
    warn "服务可能还在启动中，请稍后检查: docker compose logs"
fi

# ---- 输出结果 ----
echo ""
echo "========================================="
echo "   部署完成！"
echo "========================================="
echo ""

if [ -n "$DOMAIN" ]; then
    echo "  本地访问:  http://127.0.0.1:8090"
    echo "  域名访问:  需配置 Nginx 反代后访问 https://${DOMAIN}"
    echo ""
    echo "  Nginx 反代配置（宝塔面板 → 站点设置 → 配置文件）:"
    echo ""
    cat << NGINX
  server {
      listen 80;
      server_name ${DOMAIN};
      return 301 https://\\\$host\\\$request_uri;
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
          proxy_set_header Host \\\$host;
          proxy_set_header X-Real-IP \\\$remote_addr;
          proxy_set_header X-Forwarded-For \\\$proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto \\\$scheme;
          proxy_read_timeout 120s;
      }

      location ~ /\\. {
          deny all;
      }
  }
NGINX
else
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "服务器IP")
    echo "  访问地址: http://${LOCAL_IP}:8090"
    echo ""
    echo "  注意: 端口仅绑定 127.0.0.1，外网无法直接访问"
    echo "  如需外网访问，请配置 Nginx 反代或修改端口绑定"
fi

echo ""
echo "常用命令（在 $INSTALL_DIR 目录下执行）:"
echo "  查看日志:   docker compose logs -f"
echo "  重启服务:   docker compose restart"
echo "  停止服务:   docker compose down"
echo "  更新版本:   docker compose pull && docker compose up -d"
echo ""
