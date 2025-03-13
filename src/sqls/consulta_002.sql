SELECT 
	periodo, 
	ROUND(MIN(total),2) AS 'menor',
	ROUND(MAX(total),2) AS 'maior',
	ROUND(AVG(total),2) AS 'media'
FROM rads
WHERE situacao = 'Homologado' and total > 0.0
GROUP BY periodo
ORDER BY periodo;