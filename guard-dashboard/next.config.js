/** @type {import('next').NextConfig} */
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '..', '.env') });

const nextConfig = {
  reactStrictMode: true,
  env: {
    SMTP_SERVER: process.env.SMTP_SERVER,
    SMTP_PORT: process.env.SMTP_PORT,
    SMTP_USERNAME: process.env.SMTP_USERNAME,
    SMTP_PASSWORD: process.env.SMTP_PASSWORD,
    ALERT_FROM: process.env.ALERT_FROM,
    ALERT_TO: process.env.ALERT_TO,
    XLSX_PATH: process.env.XLSX_PATH,
  },
}

module.exports = nextConfig
