param(
  [string]$BaseUrl = 'http://localhost:3000',
  [string]$Email = 'admin@eshop.com',
  [Parameter(Mandatory = $true)][string]$Password
)

$ErrorActionPreference = 'Stop'
$api = $BaseUrl.TrimEnd('/') + '/api'
$createdId = $null
$deleted = $false

try {
  $loginBody = @{ email = $Email; password = $Password } | ConvertTo-Json -Compress
  $login = Invoke-RestMethod -Uri "$api/login" -Method Post -ContentType 'application/json' -Body $loginBody
  if (-not $login.token -or $login.user.role -ne 'admin') { throw 'Login did not return an admin JWT.' }
  $headers = @{ Authorization = "Bearer $($login.token)" }

  $categoriesBefore = Invoke-RestMethod -Uri "$api/categories" -Method Get
  $products = Invoke-RestMethod -Uri "$api/products" -Method Get
  if (@($products).Count -lt 1) { throw 'GET /api/products returned no products.' }

  $name = 'HW05_23120127_smoke_' + [guid]::NewGuid().ToString('N').Substring(0, 12)
  $createBody = @{ name = $name } | ConvertTo-Json -Compress
  $created = Invoke-RestMethod -Uri "$api/categories" -Method Post -Headers $headers -ContentType 'application/json' -Body $createBody
  $createdId = [int]$created.id
  if ($createdId -lt 1) { throw 'Create did not return a valid category id.' }

  $afterCreate = Invoke-RestMethod -Uri "$api/categories" -Method Get
  if (-not ($afterCreate | Where-Object { $_.id -eq $createdId -and $_.name -eq $name })) {
    throw 'Created category was not found in GET /api/categories.'
  }

  $updatedName = $name + '_updated'
  $updateBody = @{ name = $updatedName } | ConvertTo-Json -Compress
  $null = Invoke-RestMethod -Uri "$api/categories/$createdId" -Method Put -Headers $headers -ContentType 'application/json' -Body $updateBody
  $afterUpdate = Invoke-RestMethod -Uri "$api/categories" -Method Get
  if (-not ($afterUpdate | Where-Object { $_.id -eq $createdId -and $_.name -eq $updatedName })) {
    throw 'Updated category was not found in GET /api/categories.'
  }

  $null = Invoke-RestMethod -Uri "$api/categories/$createdId" -Method Delete -Headers $headers
  $deleted = $true
  $afterDelete = Invoke-RestMethod -Uri "$api/categories" -Method Get
  if ($afterDelete | Where-Object { $_.id -eq $createdId }) {
    throw 'Deleted category is still visible in GET /api/categories.'
  }

  [pscustomobject]@{
    checked_at = (Get-Date -Format o)
    login_role = 'admin'
    categories_before = @($categoriesBefore).Count
    products = @($products).Count
    created_id = $createdId
    create_update_delete_verified = $true
    categories_after = @($afterDelete).Count
  } | ConvertTo-Json
} finally {
  if ($createdId -and -not $deleted -and $headers) {
    try { $null = Invoke-RestMethod -Uri "$api/categories/$createdId" -Method Delete -Headers $headers } catch { Write-Warning "Cleanup failed for category ${createdId}: $_" }
  }
}
