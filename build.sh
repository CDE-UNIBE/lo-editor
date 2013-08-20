#!/bin/bash

filename="www/plugins/lo_editor.zip"
rm -rfv $filename
mkdir -v lo_editor
cp -v `find src/ | grep \.py$` lo_editor/
cp -v "src/lo-logo.png" lo_editor/
zip -9rv $filename lo_editor/
rm -rf lo_editor/
