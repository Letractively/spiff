<?
include_once dirname(__FILE__) . '/files.inc.php';

function unzip($filename, $directory)
{
  if (!$zip = zip_open($filename))
    return FALSE;
  while ($zip_entry = zip_read($zip)) {
    if (zip_entry_filesize($zip_entry) <= 0)
      continue;
    if (!zip_entry_open($zip, $zip_entry, "r"))
      continue;

    $dest_filename  = $directory . zip_entry_name($zip_entry);
    $dest_directory = dirname($dest_filename);
    mkdir_recursive($dest_directory);

    $fd   = fopen($dest_filename, 'w');
    $size = zip_entry_filesize($zip_entry);
    fwrite($fd, zip_entry_read($zip_entry, $size));
    fclose($fd);
    zip_entry_close($zip_entry);
  }
  zip_close($zip);
  return TRUE;
}
?>
