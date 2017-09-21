$argsString = ""

foreach($arg in $args){
	$argsString += $arg + " "
}

$loc = split-path $SCRIPT:MyInvocation.MyCommand.Path -parent

Invoke-Expression "python $loc\greasectl.py $argsString"