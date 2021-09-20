# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.define "windows" do |windows|
    windows.vm.box = "StefanScherer/windows_10"
    windows.vm.provision "shell",
      inline: "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))",
      privileged: true
    windows.vm.provision "shell",
      inline: "choco install python -y",
      privileged: true
    windows.vm.provision "shell",
      inline: "pip install poetry",
      privileged: true
  end
  config.vm.define "ubuntu" do |ubuntu|
    ubuntu.vm.box = "bento/ubuntu-20.04"
    ubuntu.vm.provision "shell",
      inline: "apt-get update -y && apt-get install python3.9 virtualenv pyqt5-dev pyqt5-dev-tools python3-pyqt5 qtbase5-dev libxkbcommon-x11-dev libxcomposite-dev gcc cross-gcc-dev libicu-dev python3.9-dev -y ",
      privileged: true
    ubuntu.vm.provision "shell",
      inline: "curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3.9 -",
      privileged: false
  end

end
