# Sử dụng Python 3.12 làm base image
FROM python:3.12.6

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép requirements vào thư mục làm việc
COPY requirements.txt .

# Cài đặt các dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ dự án vào thư mục làm việc
COPY . .

# Expose port 8000
EXPOSE 8000

# Chạy lệnh để khởi động server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]