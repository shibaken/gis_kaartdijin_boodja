# Node 18 Alpine Base Image
FROM node:18-alpine

# Set Working Directory
WORKDIR /app

# Install Dependencies
ADD package.json package-lock.json /app/
RUN npm ci

# Add Application
ADD . /app/
