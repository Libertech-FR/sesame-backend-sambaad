#!/bin/bash
echo "Deploiment du module sambaAD"
echo "La position determinera l'ordre d'execution des backends (comme dans init.d)"
read -p "Numero de demarrage du module (2 positions):" NUM
echo "installation dans backends/${NUM}sambaad"
INSTALL=../../backends/${NUM}sambaad
BACKEND=sambaad
if [  -d ../../backends/${NUM}${BACKEND} ];then
   read -p "Repertoire déjà existant voulez vous l'écraser ? (O/N)" -i "N" REPONSE
   if [ "$REPONSE" = "O" ];then
     rm -rf ../../backends/${NUM}${BACKEND}
   else
     exit 1
   fi
fi
mkdir ../../backends/${NUM}${BACKEND}
echo "Copie des fichiers dans ${INSTALL}"
mkdir $INSTALL/etc
cp  ./etc/* $INSTALL/etc

mkdir $INSTALL/bin
mkdir $INSTALL/lib
mkdir $INSTALL/lifecycle
PWD=`pwd`
for I in $PWD/lib/*;do
  ln -s $I $INSTALL/lib
done
for I in $PWD/bin/*;do
  ln -s $I $INSTALL/bin
done
chmod 700 $INSTALL/bin/*
cp config.yml $INSTALL
echo "Le backend a été installé dans $INSTALL"

echo "Configuration"
read -p "Url du serveur samba-ad (ldap[s]://FDQN:PORT : " HOST
read -p "Utilisateur (doit avoir les droits administrateur) : " DN
read -s -p "Mot de passe : " PASSWORD
echo ""
read -p "Base ldap : " BASE
echo "Génération du fichier de configuration"
CONFFILE=${INSTALL}/etc/config.conf
echo "host=${HOST}" > ${CONFFILE}
echo "user=${DN}" >> ${CONFFILE}
echo "password=${PASSWORD}" >> ${CONFFILE}
echo "base=${BASE}" >> ${CONFFILE}
chmod 600 ${CONFFILE}
systemctl restart sesame-daemon
echo "Vous pouvez completer le fichier de configuration avec les parametres optionnels (voir README.md)"
echo "Merci "
