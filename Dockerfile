FROM golang:1.24-alpine AS builder

WORKDIR /app
COPY sources/main.go .

# Compilation statique
RUN go build -ldflags="-s -w" -o server main.go

# Étape 2 : Image minimale FROM scratch
FROM scratch

# Copier le binaire seulement
COPY --from=builder /app/server /server

# Port exposé
EXPOSE 29785

# Commande par défaut
ENTRYPOINT ["/server"]