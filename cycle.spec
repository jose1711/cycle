%undefine _python_compile_skip_x

Name: cycle
Version: 0.3.1
Release: alt1

Summary: Calendar for women
Summary(ru_RU.KOI8-R): Календарь для женщин
License: GPL
Group: Sciences/Other
Url: http://conero.lrn.ru
Packager: Oleg Gints <go@altlinux.ru>

BuildArch: noarch
Source: %name-%version.tar.bz2

Requires: python-module-wx >= 2.5.3.1

BuildRequires: python

%description
   Possibilities of the program:
- on given length of the cycle or on typed statistics for several periods
  calculate days begin menstruation
- calculate days "safe" sex, fertile period and day to ovulations
- define d.o.b. a child
- allows to write notes
- helps to supervise reception of hormonal contraceptive tablets
%description -l ru_RU.KOI8-R
    Возможности программы:
- по заданной продолжительности цикла или по набранной статистике
  за несколько периодов спрогнозировать дни начала менструаций
- рассчитать дни "безопасного" секса, фертильный период и день овуляции
- определить дату рождения ребенка
- позволяет вести заметки
- помогает контролировать прием противозачаточных гормональных
  таблеток
%prep
%setup -n %name-%version

%build
#---- cycle ----
cat >%name <<EOF
#! /bin/sh
cd %_datadir/%name
exec ./cycle.py
EOF
#---- set_dir.py ----
cat >set_dir.py <<EOF
#generated from cycle.spec
msg_dir="%_datadir/locale"
doc_dir="%_docdir/%name-%version"
icons_dir="%_iconsdir"
bitmaps_dir="%_datadir/%name/bitmaps"
EOF

%install
%__mkdir_p $RPM_BUILD_ROOT{%_bindir,%_datadir/%name/bitmaps,%_man1dir}
%__install -p -m644 cycle.1 $RPM_BUILD_ROOT%_man1dir
%__install -p -m755 cycle $RPM_BUILD_ROOT%_bindir/%name
%__install -p -m644 *.py $RPM_BUILD_ROOT%_datadir/%name
%__install -p -m755 cycle.py $RPM_BUILD_ROOT%_datadir/%name
%__install -p -m644 bitmaps/*.* $RPM_BUILD_ROOT%_datadir/%name/bitmaps/
for d in `find msg -type d -name LC_MESSAGES`; do
    d_l=`echo $d|%__sed -e 's/msg/locale/g'`
    %__mkdir_p $RPM_BUILD_ROOT%_datadir/$d_l
    %__install -p -m644 $d/cycle.mo $RPM_BUILD_ROOT%_datadir/$d_l
done
%find_lang %name

# Menu support
mkdir -p $RPM_BUILD_ROOT{%_menudir,%_iconsdir}
mkdir -p $RPM_BUILD_ROOT{%_iconsdir/mini,%_iconsdir/large}
cat >$RPM_BUILD_ROOT%_menudir/%name <<EOF
?package(%name): \
needs=x11 \
section="Applications/Sciences/Other" \
title=Cycle \
command=%name \
icon=%name.xpm \
longtitle="Calendar for women"
EOF
install -p -m644 icons/%name.xpm $RPM_BUILD_ROOT%_iconsdir
install -p -m644 icons/mini/%name.xpm $RPM_BUILD_ROOT%_miconsdir
install -p -m644 icons/large/%name.xpm $RPM_BUILD_ROOT%_liconsdir

%add_python_compile_include %_datadir

%post
%update_menus

%postun
%clean_menus

%files -f %name.lang
%doc INSTALL CHANGELOG COPYRIGHT README* THANKS BUGS
%_bindir/%name
%_datadir/%name
%_menudir/*
%_iconsdir/*.xpm
%_miconsdir/*.xpm
%_liconsdir/*.xpm
%_man1dir/*

%changelog
* Thu Sep 15 2005 Oleg Gints <go@altlinux.ru> 0.3.1-alt1
- change to Python > 2.4 (fix problem with rotor module)
- Added man page from Miriam Ruiz <little_miry@yahoo.es>
- fix path to bytecompiling python modules

* Tue Dec 21 2004 Oleg Gints <go@altlinux.ru> 0.3.0-alt1
- change to wxPython = 2.5.X
- Add translation to the german language
  from Christian Weiske <cweiske@users.sourceforge.net>
- change install for */cycle.mo files

* Mon Oct 25 2004 Oleg Gints <go@altlinux.ru> 0.2.1-alt1
- Add colours settings

* Wed Apr 28 2004 Oleg Gints <go@altlinux.ru> 0.2.0-alt1
- Add translation for czech and slovak language
  from Jozef Riha <zefo@seznam.cz>
- change to Python 2.3
- Add description for english language
  from Marco Papa Manzillo <mpapamanz@users.sourceforge.net>

* Fri Sep 12 2003 Oleg Gints <go@altlinux.ru> 0.0.5-alt4
- add BuildRequires for build in hasher
- store source in bz2
- change tag's order

* Wed Jan 22 2003 Oleg Gints <go@altlinux.ru> 0.0.5-alt3
- again fix exception from LANGUAGE=lang1:lang2

* Fri Jan 17  2003 Oleg Gints <go@altlinux.ru> 0.0.5-alt2
- fix exception from LANGUAGE=lang1:lang2

* Mon Dec 30 2002 Oleg Gints <go@altlinux.ru> 0.0.5-alt1
- fix PopupMenu for new wxPythonGTK

* Sun Oct 27 2002 Oleg Gints <go@altlinux.ru> 0.0.4-alt2
- Change group to Sciences/Other

* Thu Oct 23 2002 Oleg Gints <go@altlinux.ru> 0.0.4-alt1
- New release
- Some spec cleanup

* Thu May 16 2002 Gints <go@ltsp.ru> 0.0.3-alt1
- Add menu

* Mon May 06 2002 Oleg Gints <go@ltsp.ru> 0.0.2-alt1
- first release

