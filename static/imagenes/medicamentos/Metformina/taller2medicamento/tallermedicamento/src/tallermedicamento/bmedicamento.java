package tallermedicamento;
import java.util.LinkedList;
public class bmedicamento {
    
    LinkedList nombre=new LinkedList();
    LinkedList cantidad=new LinkedList();
    LinkedList precio=new LinkedList();
    private Object Xprecio;
    //crear metodo para ingresar datos a la lista osea coger dat os y guardarlos en la lista
    public void IngresarDatos(String Xnombre, int Xcantidad, int Xprecio){
    
    nombre.offer(Xnombre);
    cantidad.offer(Xcantidad);
    precio.offer(Xprecio);
    }
    
    public LinkedList retornaDatos(){    
    return nombre;        
    }
    
    public LinkedList retornacantidad(){    
    return cantidad;        
    }
    
    public LinkedList retornaprecio(){    
    return precio;        
    }
    
    
}
