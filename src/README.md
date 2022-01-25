# Source/Build Directory
This folder is where extraction/processing work is done before the converted 
version is moved to the `dist` directory. Once the build process is complete you 
should have one copy of the following within this folder:

- `src/src` directory containing original source files
- `src/dist`directory containing the partials used to create the HTML files 
with `pypandoc`. 

The converted output should be available within the `dist` directory and there 
should be only one copy of each src/partial/finished item.
