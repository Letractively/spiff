<?php
  /*
  Copyright (C) 2005 Samuel Abels, <spam debain org>
  
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
  */
?>
<?php
if (!function_exists('scandir')) {
  function scandir($directory) {
    $handle = opendir($directory);
    $files  = array();
    while ($file = readdir($handle))
      if ($file != "." && $file != "..")
        array_push($files, $file);
    closedir($handle);
    return $files;
  }
}


function cpdir($src, $dest, $mode = 0775)
{   
  $dir = opendir($src);
  while ($file = readdir($dir)) {
    if ($file == '.' || $file == '..')
      continue;
   
    $src_file  = $src  . '/' . $file;
    $dest_file = $dest . '/' . $file;
    if (is_dir($src_file)) {
      mkdir($dest_file, $mode);
      cpdir($src_file, $dest_file, $mode);
      continue;
    }
    copy($src_file, $dest_file);
  }
  closedir($dir);
  return TRUE;
}


function rmdir_recursive($dir) {
  if (!$dh = @opendir($dir))
    return;
  while ($obj = readdir($dh)) {
    if ($obj == '.' || $obj == '..')
      continue;
    if (!@unlink($dir . '/' . $obj))
      rmdir_recursive($dir . '/' . $obj);
  }
  @rmdir($dir);
  return TRUE;
}


function mktmpdir($directory, $prefix, $mode = 0775)
{
  if(!file_exists($directory))
    return FALSE;
  while ($i = rand(1, getrandmax())) {
    $tmpdir = $directory . '/' . $prefix . $i;
    if (file_exists($tmpdir))
      continue;
    mkdir($tmpdir, $mode);
    return $tmpdir;
  }
  return FALSE;
}


function mkdir_recursive($directory, $mode = 0775)
{
  if(file_exists($directory))
    return FALSE;
  $parts     = explode('/', $directory);
  $directory = '';
  foreach ($parts as $part) {
    $directory .= $directory . '/';
    if (!file_exists($directory))
      mkdir($directory, $mode);
  }
  return TRUE;
}
?>
