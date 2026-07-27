# ===================== 第一阶段：构建前端 =====================
FROM node:20 AS frontend-builder

WORKDIR /app/frontend
COPY mysterycraft-web/package.json ./
RUN npm install
COPY mysterycraft-web/ ./
RUN npm run build

# ===================== 第二阶段：运行时 =====================
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt aiosqlite

# 项目代码
COPY . .

# 初始化 SQLite 数据库
RUN python data/script_db.py

# 前端 dist
COPY --from=frontend-builder /app/frontend/dist /var/www/html

# Nginx + Supervisor 配置
COPY docker/nginx.conf /etc/nginx/sites-available/default
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 9005
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
