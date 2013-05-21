#!/bin/bash

filename="lo-editor.zip"
rm -rfv $filename
mkdir -v lo-editor
cp -v `find src/ | grep \.py$` lo-editor/
cp -v "src/lo-logo.png" lo-editor/
zip -9rv $filename lo-editor/
mv -v $filname www/plugins/
rm -rf lo-editor/
