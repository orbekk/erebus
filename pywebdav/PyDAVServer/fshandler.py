
import sys
import urlparse
import os
import time
from string import joinfields, split, lower

from DAV.constants import COLLECTION, OBJECT
from DAV.errors import *
from DAV.iface import *

from DAV.davcmd import copyone, copytree, moveone, movetree, delone, deltree

class FilesystemHandler(dav_interface):
    """ 
    Model a filesystem for DAV

    This class models a regular filesystem for the DAV server

    The basic URL will be http://localhost/
    And the underlying filesystem will be /tmp

    Thus http://localhost/gfx/pix will lead
    to /tmp/gfx/pix

    """

    def __init__(self, directory, uri, verbose=False):
        self.setDirectory(directory)
        self.setBaseURI(uri)

        # should we be verbose?
        self.verbose = verbose
        self._log('Initialized with %s-%s' % (directory, uri))

    def _log(self, message):
        if self.verbose:
            print >>sys.stderr, '>> (FilesystemHandler) %s' % message

    def setDirectory(self, path):
        """ Sets the directory """

        if not os.path.isdir(path):
            raise Exception, '%s not must be a directory!' % path
        
        self.directory = path

    def setBaseURI(self, uri):
        """ Sets the base uri """

        self.baseuri = uri

    def uri2local(self,uri):
        """ map uri in baseuri and local part """

        uparts=urlparse.urlparse(uri)
        fileloc=uparts[2][1:]
        filename=os.path.join(self.directory,fileloc)
        return filename

    def local2uri(self,filename):
        """ map local filename to self.baseuri """

        pnum=len(split(self.directory,"/"))
        parts=split(filename,"/")[pnum:]
        sparts="/"+joinfields(parts,"/")
        uri=urlparse.urljoin(self.baseuri,sparts)
        return uri


    def get_childs(self,uri):
        """ return the child objects as self.baseuris for the given URI """
        
        fileloc=self.uri2local(uri)
        filelist=[]

        if os.path.exists(fileloc):
            if os.path.isdir(fileloc):
                try:
                    files=os.listdir(fileloc)
                except:
                    raise DAV_NotFound
                
                for file in files:
                    newloc=os.path.join(fileloc,file)
                    filelist.append(self.local2uri(newloc))
     
                self._log('get_childs: Childs %s' % filelist)

        return filelist

    def get_data(self,uri):
        """ return the content of an object """
        path=self.uri2local(uri)
        if os.path.exists(path):
            if os.path.isfile(path):
                s=""
                fp=open(path,"r")
                while 1:
                    a=fp.read()
                    if not a: break
                    s=s+a
                fp.close()
                self._log('Serving content of %s' % uri)
                return s
            else:
                # also raise an error for collections
                # don't know what should happen then..
                self._log('get_data: %s not found' % path)
        
        raise DAV_NotFound

    def _get_dav_resourcetype(self,uri):
        """ return type of object """
        path=self.uri2local(uri)
        if os.path.isfile(path):
            return OBJECT

        elif os.path.isdir(path):
            return COLLECTION

        raise DAV_NotFound
        
    def _get_dav_displayname(self,uri):
        #return uri
        raise DAV_Secret    # do not show

    def _get_dav_getcontentlength(self,uri):
        """ return the content length of an object """
        path=self.uri2local(uri)
        if os.path.exists(path):
            if os.path.isfile(path):
                s=os.stat(path)
                return str(s[6])
        
        return '0'

    def get_lastmodified(self,uri):
        """ return the last modified date of the object """
        path=self.uri2local(uri)
        if os.path.exists(path):
            s=os.stat(path)
            date=s[8]
            return date

        raise DAV_NotFound

    def get_creationdate(self,uri):
        """ return the last modified date of the object """
        path=self.uri2local(uri)
        if os.path.exists(path):
            s=os.stat(path)
            date=s[9]
            return date

        raise DAV_NotFound

    def _get_dav_getcontenttype(self,uri):
        """ find out yourself! """

        path=self.uri2local(uri)
        if os.path.exists(path):
            if os.path.isfile(path):
                return "application/octet-stream"
            elif os.path.isdir(path):
                return "httpd/unix-directory"

        raise DAV_NotFound, 'Could not find %s' % path

    def put(self,uri,data,content_type=None):
        """ put the object into the filesystem """
        path=self.uri2local(uri)
        try:
            fp=open(path,"w+")
            fp.write(data)
            fp.close()
            self._log('put: Created %s' % uri)
        except:
            self._log('put: Could not create %s' % uri)
            raise DAV_Error, 424

        return None

    def mkcol(self,uri):
        """ create a new collection """
        path=self.uri2local(uri)
        # remove leading slash
        if path[-1]=="/": path=path[:-1]

        # test if file already exists
        if os.path.exists(path):
            raise DAV_Error,405

        # test if parent exists
        h,t=os.path.split(path)
        if not os.path.exists(h):
            raise DAV_Error, 409

        # test, if we are allowed to create it
        try:
            os.system("mkdir '%s'" % path)
            self._log('mkcol: Created new collection %s' % path)
            return 201
        except:
            self._log('mkcol: Creation of %s denied' % path)
            raise DAV_Forbidden

    ### ?? should we do the handler stuff for DELETE, too ?
    ### (see below)

    def rmcol(self,uri):
        """ delete a collection """
        path=self.uri2local(uri)
        if not os.path.exists(path):
            raise DAV_NotFound

        if not os.system("rmdir '%s'" %path):
            return 204
        else:
            raise DAV_Forbidden # forbidden

    def rm(self,uri):
        """ delete a normal resource """
        path=self.uri2local(uri)
        if not os.path.exists(path):
            raise DAV_NotFound
        if not os.system("rm -f '%s'" %path):
            return 204
        else:
            self._log('rm: Forbidden')
            raise DAV_Forbidden # forbidden

    ###
    ### DELETE handlers (examples)
    ### (we use the predefined methods in davcmd instead of doing
    ### a rm directly
    ###

    def delone(self,uri):
        """ delete a single resource 

        You have to return a result dict of the form
        uri:error_code
        or None if everything's ok
        
        """
        return delone(self,uri)

    def deltree(self,uri):
        """ delete a collection 

        You have to return a result dict of the form
        uri:error_code
        or None if everything's ok
        """

        return deltree(self,uri)


    ###
    ### MOVE handlers (examples)
    ###

    def moveone(self,src,dst,overwrite):
        """ move one resource with Depth=0 

        an alternative implementation would be

        result_code=201
        if overwrite: 
            result_code=204
            r=os.system("rm -f '%s'" %dst)
            if r: return 412
        r=os.system("mv '%s' '%s'" %(src,dst))
        if r: return 412
        return result_code
       
        (untested!). This would not use the davcmd functions
        and thus can only detect errors directly on the root node.
        """
        return moveone(self,src,dst,overwrite)

    def movetree(self,src,dst,overwrite):
        """ move a collection with Depth=infinity

        an alternative implementation would be

        result_code=201
        if overwrite: 
            result_code=204
            r=os.system("rm -rf '%s'" %dst)
            if r: return 412
        r=os.system("mv '%s' '%s'" %(src,dst))
        if r: return 412
        return result_code
       
        (untested!). This would not use the davcmd functions
        and thus can only detect errors directly on the root node"""

        return movetree(self,src,dst,overwrite)

    ###
    ### COPY handlers
    ###

    def copyone(self,src,dst,overwrite):
        """ copy one resource with Depth=0 

        an alternative implementation would be

        result_code=201
        if overwrite: 
            result_code=204
            r=os.system("rm -f '%s'" %dst)
            if r: return 412
        r=os.system("cp '%s' '%s'" %(src,dst))
        if r: return 412
        return result_code
       
        (untested!). This would not use the davcmd functions
        and thus can only detect errors directly on the root node.
        """
        return copyone(self,src,dst,overwrite)

    def copytree(self,src,dst,overwrite):
        """ copy a collection with Depth=infinity

        an alternative implementation would be

        result_code=201
        if overwrite: 
            result_code=204
            r=os.system("rm -rf '%s'" %dst)
            if r: return 412
        r=os.system("cp -r '%s' '%s'" %(src,dst))
        if r: return 412
        return result_code
       
        (untested!). This would not use the davcmd functions
        and thus can only detect errors directly on the root node"""

        return copytree(self,src,dst,overwrite)

    ###
    ### copy methods.
    ### This methods actually copy something. low-level
    ### They are called by the davcmd utility functions
    ### copytree and copyone (not the above!)
    ### Look in davcmd.py for further details.
    ###

    def copy(self,src,dst):
        """ copy a resource from src to dst """
        srcfile=self.uri2local(src)
        dstfile=self.uri2local(dst)
        try:
            os.system("cp '%s' '%s'" %(srcfile,dstfile))
        except:
            self._log('copy: forbidden')
            raise DAV_Error, Forbidden

    def copycol(self,src,dst):
        """ copy a collection.

        As this is not recursive (the davserver recurses itself)
        we will only create a new directory here. For some more
        advanced systems we might also have to copy properties from
        the source to the destination.
        """

        return self.mkcol(dst)


    def exists(self,uri):
        """ test if a resource exists """
        path=self.uri2local(uri)
        if os.path.exists(path):
            return 1
        return None

    def is_collection(self,uri):
        """ test if the given uri is a collection """
        path=self.uri2local(uri)
        if os.path.isdir(path):
            return 1
        else:
            return 0

