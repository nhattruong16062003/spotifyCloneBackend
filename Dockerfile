# Sử dụng image Python chính thức với phiên bản 3.12.6-slim
FROM python:3.12.6-slim

# Cài các package hệ thống cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy requirements trước để tận dụng cache
COPY requirements.txt .

# Cài đặt dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --default-timeout=150 -r requirements.txt

# Copy toàn bộ mã nguồn
COPY . .

# Thiết lập biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Mở cổng 8000
EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh

# Đảm bảo entrypoint có quyền thực thi
RUN chmod +x /entrypoint.sh

# Chạy ứng dụng
CMD ["/entrypoint.sh"]