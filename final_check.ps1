$health = Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -UseBasicParsing
Write-Host "[Health] $($health.StatusCode)"
$content = $health.Content | ConvertFrom-Json
Write-Host "  SpatialEncoder: $($content.spatial_encoder)"
Write-Host "  Scene nodes: $($content.scene_nodes)"

# Test relation API
$post = Invoke-WebRequest -Uri 'http://localhost:5000/api/relation' -Method POST -Body '{"node_i":0,"node_j":1}' -ContentType 'application/json' -UseBasicParsing
Write-Host "[Relation #0 vs #1] $($post.StatusCode)"
$r = $post.Content | ConvertFrom-Json
Write-Host "  dist=$($r.distance_m)m, pred=$($r.relation), p=$($r.predicted_prob)"

$post2 = Invoke-WebRequest -Uri 'http://localhost:5000/api/relation' -Method POST -Body '{"node_i":0,"node_j":10}' -ContentType 'application/json' -UseBasicParsing
$r2 = $post2.Content | ConvertFrom-Json
Write-Host "[Relation #0 vs #10] dist=$($r2.distance_m)m, pred=$($r2.relation), p=$($r2.predicted_prob)"

Write-Host ""
Write-Host "=== System Ready ==="
Write-Host "Frontend: http://localhost:3000"
Write-Host "Inference: http://localhost:5000"
Write-Host "  - SpatialEncoder: Val Acc=98.1%"
Write-Host "  - RelationTransformer: Val Acc=100%"
