FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* pnpm-workspace.yaml* ./

# Install dependencies using npm (since there is a package-lock.json)
RUN npm install

# Copy application code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run Vite development server bound to all interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
