SELECT *
FROM rads, servidores
WHERE  rads.siape = servidores.siape and situacao = 'Homologado' and (total > 0 and total < 10)