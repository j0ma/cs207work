#########################
# LightCurve Module	#
# Computer Science 207	#
# (c) Jonne Saleva	#
#########################


from collections import defaultdict
import itertools
import reprlib
import os

# Function for parsing LightCurves
def lc_reader2(filename):
    """
    Description
    -----------
    Reads in light curves from file
    
    Parameters
    ----------
    filename: str
        name of file
        
    Returns
    -------
    Tuple containing a list of values and metadata dict.
    """
    values_list = []
    with open(filename) as fp:
        
        # parse first two lines for the facet values
        fac_names, fac_values = [next(fp).replace('#', '').split() for _ in range(2)]
        
        # convert values to float if possible
        # note: this is a hacky way; i would be 
        # very interested in knowing a better one!
        # (or condensing this to an anon. function etc.)
        def conv_value(val):
            """
            Description
            -----------
            Function for parsing facet values.
            Converts numeric values to floats,
            and ignores the rest.
            
            Parameters
            ----------
            val: parameter to parse
            
            Returns
            -------
            Converted `val`
            """
            try:
                out = float(val)
            except:
                out = val
            return out
        
        dict_of_facets = {n:conv_value(v) for n,v in zip(fac_names, fac_values)}
        
        # parse rest of file
        for line in fp:
            if line.find('#')!=0:
                values_list.append([float(f) for f in line.strip().split()])
    
    return (values_list, dict_of_facets)


# Light Curve Class
class LightCurve:
    
    def __init__(self, data, metadict):
        self._time = [x[0] for x in data]
        self._amplitude = [x[1] for x in data]
        self._error = [x[2] for x in data]
        self.metadata = metadict
        self.filename = None
    
    @classmethod
    def from_file(cls, filename):
        """
        Description
        -----------
        Class method for generating `LightCurve` instances.
        
        Parameters
        ----------
        cls: class name
        filename: str
            file to parse
        """
        lclist, metadict = lc_reader2(filename)
        instance = cls(lclist, metadict)
        instance.filename = filename
        return instance
    
    def __repr__(self):
        """
        Description
        -----------
        Method for generating a neat string representation of the class
        
        Parameters
        ----------
        self: LightCurve instance
        
        Returns
        -------
        String representation of the class
        """
        class_name = type(self).__name__
        components = reprlib.repr(list(itertools.islice(self.timeseries,0,10)))
        components = components[components.find('['):]
        return '{}({})'.format(class_name, components)        
        
    def __getitem__(self, ind):
        """
        Description
        -----------
        Mandatory indexing method for sequences
        
        Parameters
        ----------
        self: LightCurve instance
        ind: int
            index of desired element
        
        Returns
        -------
        A tuple (time, amplitude) corresponding to the
        correct index.
        """
        return (self._time[ind], self._amplitude[ind])
    
    def __len__(self):
        """
        Description
        -----------
        Mandatory length method for sequences
        
        Parameters
        ----------
        self: LightCurve instance
        
        Returns
        -------
        length of `_time` attribute
        """
        
        # we cheat and use the len() method for lists,
        # which is what our _time elements are!
        return len(self._time)
    
    # time property
    @property
    def time(self):
        """
        Description
        -----------
        Getter method for read-only property `time`
        
        Parameters
        ----------
        self: LightCurve instance
        
        Returns
        -------
        property `self._time`
        """
        return self._time
    
    # amplitude property
    @property
    def amplitude(self):
        """
        Description
        -----------
        Getter method for read-only property `amplitude`
        
        Parameters
        ----------
        self: LightCurve instance
        
        Returns
        -------
        property `self._amplitude`
        """
        return self._amplitude
    
    # timeseries property
    @property
    def timeseries(self):
        """
        Description
        -----------
        Getter method tfor read-only property `timeseries`
        
        Parameters
        ----------
        self: LightCurve instance
        
        Returns
        -------
        iterator over (time, amplitude) tuples
        """
        return zip(self._time, self._amplitude)



# Light Curve Database Class
class LightCurveDB:
    
    def __init__(self):
        self._collection={}
        self._field_index=defaultdict(list)
        self._tile_index=defaultdict(list)
        self._color_index=defaultdict(list)
    
    def populate(self, folder):
        """
        Description
        -----------
        Reads `.mjd` files and parses them
        into LightCurve instances in self._collection
        
        Parameters
        ----------
        self: LightCurveDB instance
        folder: str
            folder to search for .mjd files in
        """
        for root,dirs,files in os.walk(folder): # DEPTH 1 ONLY
            for file in files:
                if file.find('.mjd')!=-1:
                    the_path = root+"/"+file
                    self._collection[file] = LightCurve.from_file(the_path)
    
    def index(self):
        """
        Description
        -----------
        Creates three indices based on 
        `field`, `tile`, and `color`.
        
        Parameters
        ----------
        self: LightCurveDB instance
        
        Returns
        -------
        None
        """
        for f in self._collection:
            lc, tilestring, seq, color, _ = f.split('.')
            field = int(lc.split('_')[-1])
            tile = int(tilestring)
            self._field_index[field].append(self._collection[f])
            self._tile_index[tile].append(self._collection[f])
            self._color_index[color].append(self._collection[f])
     
    def retrieve(self, facet, value):
        """
        Description
        -----------
        Selects the appropriate index
        based on `facet` and retrieves
        the light curve according to `value`
        of that `facet`.
        
        Parameters
        ----------
        self: LightCurveDB instance
        
        facet: string
            facet to use in look up
            nb: must be one of (`field`, `tile`, `color`)
        
        value: string/int
            value of facet. type depends on `facet`
            
        Returns
        -------
        lc_out: LightCurve instance
        """
        
        # wrap all indices in a dict
        index_dict = {
            'field': self._field_index,
            'tile': self._tile_index,
            'color': self._color_index
        }
        
        # validate user input for `facet`
        assert facet in index_dict.keys(),\
        'ERROR: Facet can only be `field`, `tile`, or `color`'
        
        # return correct light curve
        lc_out = index_dict[facet][value]
        return lc_out
    
