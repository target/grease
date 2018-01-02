$argsString = ""

foreach($arg in $args){
	$argsString += $arg + " "
}

$loc = split-path $SCRIPT:MyInvocation.MyCommand.Path -parent

python "$loc\grease" $argsString