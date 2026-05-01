$tests = @(@{i=0;j=1}, @{i=0;j=10}, @{i=0;j=50}, @{i=10;j=50}, @{i=50;j=100}, @{i=0;j=150})
foreach ($t in $tests) {
    $post = [System.Net.HttpWebRequest]::Create('http://localhost:5000/api/relation')
    $post.Method = 'POST'
    $post.ContentType = 'application/json'
    $body = [System.Text.Encoding]::UTF8.GetBytes("{`"node_i`":$($t.i),`"node_j`":$($t.j)}")
    $post.GetRequestStream().Write($body, 0, $body.Length)
    $post.GetRequestStream().Close()
    $presp = $post.GetResponse()
    $pstream = $presp.GetResponseStream()
    $preader = [System.IO.StreamReader]::new($pstream)
    $r = $preader.ReadToEnd() | ConvertFrom-Json
    Write-Host "Node $($t.i) vs $($t.j): dist=$($r.distance_m)m, pred=$($r.relation), p=$([math]::Round($r.predicted_prob, 3))"
}
Write-Host "`nAll tests complete!"
