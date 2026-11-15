"""Limites que definem dia de geada, calor, seca e chuva forte (fonte: data/rag/metodologia-indicadores.md)."""

# Risco de geada: dia com temperatura mínima do ar abaixo de 2 °C.
TMIN_GEADA_C = 2.0

# Dias de calor forte: Tmax acima de 35 °C quando a cultura não tem limite próprio.
TMAX_CALOR_C = 35.0

# Veranico: dia seco é o que tem menos de 1 mm de chuva (o veranico em si é uma sequência de 10 dias ou mais).
CHUVA_DIA_SECO_MM = 1.0

# Chuva forte: dia acima do percentil 95 da chuva dos dias com chuva (>= 1 mm) do período-base.
PERCENTIL_CHUVA_FORTE = 95
BASE_INICIO = 1991
BASE_FIM = 2020
