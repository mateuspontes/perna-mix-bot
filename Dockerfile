# Build stage
FROM rust:1.75 as builder

WORKDIR /app

# Copy manifests
COPY Cargo.toml ./

# Copy source code
COPY src ./src

# Build for release
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install necessary runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the binary from builder
COPY --from=builder /app/target/release/perna-mix-bot /app/perna-mix-bot

# Expose port for health checks
EXPOSE 10000

# Set the PORT environment variable (Render default)
ENV PORT=10000

# Run the bot
CMD ["/app/perna-mix-bot"]
