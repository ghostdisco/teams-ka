#!/bin/sh

{
    brew install google-chrome
} || {
    echo 'Homebrew must be installed to continue...'
    exit 1
}
