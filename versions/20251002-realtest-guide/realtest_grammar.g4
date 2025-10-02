grammar RealTest;

script  : line* EOF ;
line    : statement? NEWLINE ;

statement
        : comment
        | keyvalue
        | keyonly
        | textline
        ;

keyvalue: WS? KEY ':' WS? VALUE? ;
keyonly : WS? KEY ':' ;
textline: WS? TEXT ;
comment : WS? COMMENT ;

KEY     : [A-Za-z] [A-Za-z0-9_.?]* ;
VALUE   : ~[\r\n]+ ;
TEXT    : ~[:\r\n] ~[\r\n]* ;
COMMENT : '//' ~[\r\n]* ;
WS      : [ \t]+ -> skip ;
NEWLINE : '\r'? '\n' ;
