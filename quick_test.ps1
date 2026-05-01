$req = [System.Net.HttpWebRequest]::Create('http://localhost:5000/api/health')
$resp = $req.GetResponse()
$stream = $resp.GetResponseStream()
$reader = [System.IO.StreamReader]::new($stream)
$content = $reader.ReadToEnd()
Write-Host "Health: $content"

# Test relation API
$post = [System.Net.HttpWebRequest]::Create('http://localhost:5000/api/relation')
$post.Method = 'POST'
$post.ContentType = 'application/json'
$body = [System.Text.Encoding]::UTF8.GetBytes('{"node_i":0,"node_j":1}')
$post.GetRequestStream().Write($body, 0, $body.Length)
$post.GetRequestStream().Close()
$presp = $post.GetResponse()
$pstream = $presp.GetResponseStream()
$preader = [System.IO.StreamReader]::new($pstream)
Write-Host "Relation: $($preader.ReadToEnd())"
