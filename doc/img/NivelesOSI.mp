% Metapost TeX macro
% Title: /home/edorka/blas/doc/img/NivelesOSI.dia
% Creator: Dia v0.96.1
% CreationDate: Sat Jun 28 21:42:06 2008
% For: edorka


beginfig(1);
verbatimtex
%&latex
\documentclass{minimal}
\begin{document}
etex
% Define macro for horizontal centering.
vardef hcentered primary P =
  P shifted -(xpart center P, 0)
enddef;
% Define macro for right justification.
vardef rjust primary P =
  P shifted -(xpart (lrcorner P - llcorner P), 0)
enddef;
  % picture(16.950000,-19.050000)(24.050000,-4.950000)
  x = 1.000000cm; y = -1.000000cm;

  t = 1.000000;

% set_line_color 0.000000, 0.000000, 0.000000
% set_line_color 1.000000, 1.000000, 1.000000
  path p;
  p = (17.000000x,5.000000y)--(17.000000x,7.000000y)--(24.000000x,7.000000y)--(24.000000x,5.000000y)--cycle;
  fill p withcolor (0.854902,0.854902,0.854902);
% set_linewidth 0.100000
% set_line_color 0.000000, 0.000000, 0.000000
  draw (17.000000x,5.000000y)--(17.000000x,7.000000y)--(24.000000x,7.000000y)--(24.000000x,5.000000y)--cycle
    withpen pencircle scaled 0.1000x;
% set_line_color 0.000000, 0.000000, 0.000000
  draw hcentered btex {\usefont{OT1}{phv}{b}{n} Aplicación} etex scaled 1.64t shifted (20.500000x,6.142500y);
  path p;
  p = (17.000000x,7.000000y)--(17.000000x,9.000000y)--(24.000000x,9.000000y)--(24.000000x,7.000000y)--cycle;
  fill p withcolor (1.000000,1.000000,1.000000);
% set_linewidth 0.100000
% set_line_color 0.000000, 0.000000, 0.000000
  draw (17.000000x,7.000000y)--(17.000000x,9.000000y)--(24.000000x,9.000000y)--(24.000000x,7.000000y)--cycle
    withpen pencircle scaled 0.1000x;
% set_line_color 0.000000, 0.000000, 0.000000
  draw hcentered btex {\usefont{OT1}{phv}{m}{n} Presentación} etex scaled 1.64t shifted (20.500000x,8.142500y);
  path p;
  p = (17.000000x,9.000000y)--(17.000000x,11.000000y)--(24.000000x,11.000000y)--(24.000000x,9.000000y)--cycle;
  fill p withcolor (1.000000,1.000000,1.000000);
% set_linewidth 0.100000
% set_line_color 0.000000, 0.000000, 0.000000
  draw (17.000000x,9.000000y)--(17.000000x,11.000000y)--(24.000000x,11.000000y)--(24.000000x,9.000000y)--cycle
    withpen pencircle scaled 0.1000x;
% set_line_color 0.000000, 0.000000, 0.000000
  draw hcentered btex {\usefont{OT1}{phv}{m}{n} Sesión} etex scaled 1.64t shifted (20.500000x,10.142500y);
  path p;
  p = (17.000000x,11.000000y)--(17.000000x,13.000000y)--(24.000000x,13.000000y)--(24.000000x,11.000000y)--cycle;
  fill p withcolor (1.000000,1.000000,1.000000);
% set_linewidth 0.100000
% set_line_color 0.000000, 0.000000, 0.000000
  draw (17.000000x,11.000000y)--(17.000000x,13.000000y)--(24.000000x,13.000000y)--(24.000000x,11.000000y)--cycle
    withpen pencircle scaled 0.1000x;
% set_line_color 0.000000, 0.000000, 0.000000
  draw hcentered btex {\usefont{OT1}{phv}{m}{n} Transporte} etex scaled 1.64t shifted (20.500000x,12.142500y);
  path p;
  p = (17.000000x,13.000000y)--(17.000000x,15.000000y)--(24.000000x,15.000000y)--(24.000000x,13.000000y)--cycle;
  fill p withcolor (1.000000,1.000000,1.000000);
% set_linewidth 0.100000
% set_line_color 0.000000, 0.000000, 0.000000
  draw (17.000000x,13.000000y)--(17.000000x,15.000000y)--(24.000000x,15.000000y)--(24.000000x,13.000000y)--cycle
    withpen pencircle scaled 0.1000x;
% set_line_color 0.000000, 0.000000, 0.000000
  draw hcentered btex {\usefont{OT1}{phv}{m}{n} Red} etex scaled 1.64t shifted (20.500000x,14.142500y);
  path p;
  p = (17.000000x,15.000000y)--(17.000000x,17.000000y)--(24.000000x,17.000000y)--(24.000000x,15.000000y)--cycle;
  fill p withcolor (1.000000,1.000000,1.000000);
% set_linewidth 0.100000
% set_line_color 0.000000, 0.000000, 0.000000
  draw (17.000000x,15.000000y)--(17.000000x,17.000000y)--(24.000000x,17.000000y)--(24.000000x,15.000000y)--cycle
    withpen pencircle scaled 0.1000x;
% set_line_color 0.000000, 0.000000, 0.000000
  draw hcentered btex {\usefont{OT1}{phv}{m}{n} Enlace} etex scaled 1.64t shifted (20.500000x,16.142500y);
  path p;
  p = (17.000000x,17.000000y)--(17.000000x,19.000000y)--(24.000000x,19.000000y)--(24.000000x,17.000000y)--cycle;
  fill p withcolor (1.000000,1.000000,1.000000);
% set_linewidth 0.100000
% set_line_color 0.000000, 0.000000, 0.000000
  draw (17.000000x,17.000000y)--(17.000000x,19.000000y)--(24.000000x,19.000000y)--(24.000000x,17.000000y)--cycle
    withpen pencircle scaled 0.1000x;
% set_line_color 0.000000, 0.000000, 0.000000
  draw hcentered btex {\usefont{OT1}{phv}{m}{n} Física} etex scaled 1.64t shifted (20.500000x,18.142500y);
endfig;
end;
