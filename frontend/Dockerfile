FROM node:20-alpine

WORKDIR /app

# Sao chép package.json để cài đặt thư viện
COPY package.json ./

RUN npm install --legacy-peer-deps

# Sao chép toàn bộ mã nguồn
COPY . .

# Mở port 3000
EXPOSE 3000

# Lệnh khởi chạy server dev của Next.js
CMD ["npm", "run", "dev"]
