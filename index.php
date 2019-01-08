<?php
require 'vendor/autoload.php';
header("Access-Control-Allow-Origin:*");
date_Default_timezone_set("PRC");

use Qiniu\Auth;
use Qiniu\Storage\UploadManager;

$content = $_REQUEST['content'];
$velocity = $_REQUEST['velocity'];
$source = $_REQUEST['source']; //1男中音 3女高音 5女中音
$genre = $_REQUEST['genre']; //0 流行 1 民谣 2 摇滚 3 电子
$emotion = $_REQUEST['emotion']; // 0 开心 1 伤心
// echo '|content:' . $content . ';velocity:' . $velocity . ';source:' . $source . ';genre:' . $genre . ';emotion:' . $emotion . "\n";

$rate = rand(5, 8) / 10;
$name = md5(uniqid());
$url = "";
$content = replace_specialChar($content);
$content = replace_space($content);
// $contents = separate($content);
$contents = explode(",", $content);
$size = sizeof($contents);
if ($size > 16 || $size == 1 || $size == 7 || $size == 11 || $size == 13 || $size == 14 || $size == 15) {
    $data = array(
        'mp3File' => '',
        'success' => 0,
    );
    echo json_encode($data);

    return;
}

$zhugesize = get_zhugesize($size);
$fugesize = $size - $zhugesize;
$zhugecount = $fugecount = "";
$count = array();
$geci = '';
$lrc = '';
for ($i = 0; $i < $size; $i++) {
    $newStr = $contents[$i];
    $count[$i] = mb_strlen($newStr, "utf-8");
    $geci = $geci . $newStr;
    if ($lrc) {
        $lrc = $lrc . "," . $newStr;
    } else {
        $lrc = $newStr;
    }
    if ($i < $zhugesize) { // 进位取整
        $zhugecount = $zhugecount . $count[$i] . ",";
    } else {
        $fugecount = $fugecount . $count[$i] . ",";
    }
}
$gecicount = 0;
$tag = 0;
foreach ($count as $key => $value) {
    $gecicount = $gecicount + $value;
}
if (strlen($zhugecount) > 0 && strlen($fugecount) > 0) {
    $zhugecount = substr($zhugecount, 0, strlen($zhugecount) - 1);
    $fugecount = substr($fugecount, 0, strlen($fugecount) - 1);
}
// $velocity = 100 - (int) ($gecicount / $size) * 5 + $rate * 120;
if ($source == 1) {
    $melody_range_a = "35,47";
    $melody_range_b = "35,48";
} else if ($source == 2) {
    $melody_range_a = "35,48";
    $melody_range_b = "35,50";
} else if ($source == 3) {
    $melody_range_a = "47,60";
    $melody_range_b = "47,65";
} else if ($source == 4) {
    $melody_range_a = "47,59";
    $melody_range_b = "47,60";
} else if ($source == 5) {
    $melody_range_a = "47,59";
    $melody_range_b = "47,60";
} else if ($source == 6) {
    $melody_range_a = "47,59";
    $melody_range_b = "47,60";
}
// echo 'sh ./run_h5.sh ' . $name . ' ' . $zhugecount . ' ' . $fugecount . ' ' . $gecicount . ' ' . $geci . ' ' . $velocity . ' ' . $source . ' ' . $melody_range_a . ' ' . $melody_range_b . ' ' . $genre . ' ' . $emotion . ' ' . $zhugesize . ' ' . $fugesize . ' 2>&1';
exec('sh /opt/lampp/htdocs/code/scripts/run_h5.sh ' . $name . ' ' . $zhugecount . ' ' . $fugecount . ' ' . $gecicount . ' ' . $geci . ' ' . $velocity . ' ' . $source . ' ' . $melody_range_a . ' ' . $melody_range_b . ' ' . $genre . ' ' . $emotion . ' ' . $zhugesize . ' ' . $fugesize . ' 2>&1', $result, $status);
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
        $mp3File = "http://ai.mojing.cn/".$key;
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

function depart(&$result, $count, $str)
{
    if ($count <= 13) {
        array_push($result, $str);
        return;
    }
    $str1 = mb_substr($str, 0, (int) ($count / 2), "utf-8");
    depart($result, (int) ($count / 2) + 1, $str1);
    $str2 = mb_substr($str, (int) ($count / 2), $count - 1, "utf-8");
    depart($result, (int) ($count / 2), $str2);
}

function separate($content)
{
    $contents = explode(",", $content);
    $contents = array_filter($contents);
    $size = sizeof($contents);
    if ($size == 1) {
        $content = $content . "," . $content;
        $contents = explode(",", $content);
        $size = sizeof($contents);
    }
    $result = array();
    for ($i = 0; $i < $size; $i++) {
        $str = $contents[$i];
        $count = mb_strlen($str, "utf-8");
        if ($i + 1 < $size) {
            $strnext = $contents[$i + 1];
            $countnext = mb_strlen($strnext, "utf-8");
            // 合短句
            if ($size > 4 && $countnext < 6 && $count < 6) {
                array_push($result, $str . $strnext);
                $i = $i + 1;
                continue;
            }
        }
        if ($count == 1) {
            $str = $str . $str;
        }
        // 拆长句
        depart($result, $count, $str);
    }

    $newsize = sizeof($result);
    while ($newsize == 7 || $newsize == 11 || $newsize == 13 || $newsize == 14 || $newsize == 15) {
        $maxcount = 0;
        $maxi = 0;
        for ($i = 0; $i < $newsize; $i++) {
            $str = $result[$i];
            $count = mb_strlen($str, "utf-8");
            if ($count > $maxcount) {
                $maxcount = $count;
                $maxi = $i;
            }
        }

        $maxstr = $result[$maxi];
        $str1 = mb_substr($maxstr, 0, (int) ($maxcount / 2), "utf-8");
        $str2 = mb_substr($maxstr, (int) ($maxcount / 2), (int) ($maxcount / 2) + 1, "utf-8");
        for ($i = $newsize; $i > $maxi + 1; $i--) {
            $result[$i] = $result[$i - 1];
        }
        $result[$maxi] = $str1;
        $result[$maxi + 1] = $str2;
        $newsize = sizeof($result);
    }
    return $result;
}

function get_zhugesize($num)
{
    if ($num == 1) {
        return 1;
    } else
    if ($num == 2) {
        return 1;
    } else
    if ($num == 3) {
        return 2;
    } else
    if ($num == 4) {
        return 2;
    } else
    if ($num == 5) {
        return 4;
    } else
    if ($num == 6) {
        return 4;
    } else
    if ($num == 8) {
        return 4;
    } else
    if ($num == 9) {
        return 8;
    } else
    if ($num == 10) {
        return 8;
    } else
    if ($num == 12) {
        return 8;
    } else
    if ($num == 16) {
        return 8;
    } else {
        return 1;
    }
}

function replace_specialChar($strParam)
{
    $regex = "/\/|\～|\，|\。|\！|\？|\“|\”|\【|\】|\『|\』|\：|\；|\《|\》|\’|\‘|\ |\·|\~|\!|\@|\#|\\$|\%|\^|\&|\*|\(|\)|\_|\+|\{|\}|\:|\<|\>|\?|\[|\]|\,|\.|\/|\;|\'|\`|\-|\=|\\\|\|/";
    return preg_replace($regex, ",", $strParam);
}

function replace_space($str)
{
    $search = array(" ", "　", "\n", "\r", "\t");
    $replace = array("", "", "", "", "");
    return str_replace($search, $replace, $str);
}
