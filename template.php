<?php
require 'vendor/autoload.php';
header("Access-Control-Allow-Origin:*");
date_Default_timezone_set("PRC");

use Qiniu\Auth;
use Qiniu\Storage\UploadManager;

$content = $_REQUEST['content'];
$source = $_REQUEST['source'];
$template_num = $_REQUEST['template_num'];

$name = md5(uniqid());
$url = "";
$content = replace_specialChar($content);
$content = replace_space($content);
$gecicount = mb_strlen($content, "utf-8");


exec('sh /opt/lampp/htdocs/code/scripts/run_template.sh ' . $name . ' ' . $gecicount . ' ' . $content . ' ' . $template_num . ' ' . $source . ' 2>&1', $result, $status);
// print_r($result);

$mp3File = '';
$success = 0;

if ($status == 0) {
    $accessKey = 'JCYcOc_dLoCag3mmdCFLa_GujdrKrooX96IbeF0N';
    $secretKey = '7s0pz2cTpOxE-wDddiLEu8hI3UpK5oQi-mvg0Ed3';
    $auth = new Auth($accessKey, $secretKey);
    $bucket = '2018';
// 生成上传Token
    $token = $auth->uploadToken($bucket);
// 构建 UploadMan
    // 要上传文件的本地路径
    $filePath = '/home/root/music/mp3/' . $name . ".mp3";
// 上传到七牛后保存的文件名
    $key = "wyxg/" . date("Ymd") . "/" . $name . ".mp3";
// 初始化 UploadManager 对象并进行文件的上传。
    $uploadMgr = new UploadManager();
// 调用 UploadManager 的 putFile 方法进行文件的上传。
    list($ret, $err) = $uploadMgr->putFile($token, $key, $filePath);
    if ($err !== null) {
        echo $err;
        $status = 1;
    } else {
        $mp3File = "http://ai.mojing.cn/" . $key;
    }
} else {
    echo "process failed";
}
if ($status == 0) {
    $success = 1;
}
$data = array(
    'mp3File' => $mp3File,
    'success' => $success,
);

echo json_encode($data);


function replace_specialChar($strParam)
{
    $regex = "/\/|\，|\。|\！|\？|\“|\”|\【|\】|\『|\』|\：|\；|\《|\》|\’|\‘|\ |\·|\,|\~|\!|\@|\#|\\$|\%|\^|\&|\*|\(|\)|\_|\+|\{|\}|\:|\<|\>|\?|\[|\]|\,|\.|\/|\;|\'|\`|\=|\\\|\|/";
    return preg_replace($regex, "", $strParam);
}

function replace_space($str)
{
    $search = array(" ", "　", "\n", "\r", "\t");
    $replace = array("", "", "", "", "");
    return str_replace($search, $replace, $str);
}
