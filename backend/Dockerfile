# Sử dụng base image Python gọn nhẹ
FROM python:3.12-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Thiết lập các biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cài đặt các gói hệ thống cần thiết (nếu cần compile psycopg2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các thư viện Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Sao chép mã nguồn backend vào container
COPY . /app/

# Mở port 8000
EXPOSE 8000

# Chạy server phát triển của Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
