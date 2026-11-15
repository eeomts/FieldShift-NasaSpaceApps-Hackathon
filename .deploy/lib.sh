# Funções comuns aos scripts da .deploy (use com: . .deploy/lib.sh)

# carregar_env <local|producao>: lê .deploy/env/<ambiente>.env e exporta CHAVE=valor, sem executar nada
carregar_env() {
    case "${1:-}" in
        local|producao) AMBIENTE=$1 ;;
        *)
            echo "erro: ambiente deve ser 'local' ou 'producao'" >&2
            exit 1
            ;;
    esac

    ENV_FILE=".deploy/env/$AMBIENTE.env"
    if [ ! -f "$ENV_FILE" ]; then
        echo "erro: $ENV_FILE nao existe." >&2
        echo "  cp .deploy/env/exemplo.env $ENV_FILE   e preencha antes de subir" >&2
        exit 1
    fi

    while IFS= read -r linha || [ -n "$linha" ]; do
        linha=$(printf '%s' "$linha" | tr -d '\r')
        case "$linha" in
            ''|'#'*) continue ;;
        esac
        chave=${linha%%=*}
        valor=${linha#*=}
        case "$chave" in
            *[!A-Z0-9_]*|[0-9]*|'')
                echo "erro: linha invalida em $ENV_FILE: $chave" >&2
                exit 1
                ;;
        esac
        case "$valor" in
            \"*\") valor=${valor#\"}; valor=${valor%\"} ;;
            \'*\') valor=${valor#\'}; valor=${valor%\'} ;;
        esac
        export "$chave=$valor"
    done < "$ENV_FILE"

    export AMBIENTE ENV_FILE
    DB_PORT=${DB_PORT:-5432}
    export DB_PORT
}

# exigir VAR...: para com erro se alguma estiver vazia
exigir() {
    for var in "$@"; do
        eval "valor=\${$var:-}"
        if [ -z "$valor" ]; then
            echo "erro: $var esta vazio em $ENV_FILE" >&2
            exit 1
        fi
    done
}

# pg <programa> [args]: roda pg_dump/psql contra o banco do ambiente (no compose ou externo); stdin passa direto
pg() {
    programa=$1
    shift
    if [ "$DB_HOST" = "db" ]; then
        ./.deploy/agroai "$AMBIENTE" exec -T -e PGPASSWORD="$DB_PASSWORD" db \
            "$programa" -U "$DB_USER" -d "$DB_NAME" "$@"
    else
        docker run --rm -i -e PGPASSWORD="$DB_PASSWORD" --add-host host.docker.internal:host-gateway \
            postgres:17-alpine "$programa" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" "$@"
    fi
}
