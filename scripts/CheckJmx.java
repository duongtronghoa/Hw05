import java.io.File;
import org.apache.jmeter.util.JMeterUtils;
import org.apache.jmeter.save.SaveService;

public class CheckJmx {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.out.println("Usage: java CheckJmx <jmeter_home> <jmx_files...>");
            return;
        }
        String jmeterHome = args[0];
        File props = new File(jmeterHome, "bin/jmeter.properties");
        JMeterUtils.setJMeterHome(jmeterHome);
        JMeterUtils.loadJMeterProperties(props.getAbsolutePath());
        SaveService.loadProperties();
        
        for (int i = 1; i < args.length; i++) {
            File f = new File(args[i]);
            try {
                Object tree = SaveService.loadTree(f);
                if (tree != null) {
                    System.out.println("LOADED_OK: " + f.getName());
                } else {
                    System.err.println("FAILED_NULL: " + f.getName());
                }
            } catch (Throwable t) {
                System.err.println("FAILED_EXCEPTION: " + f.getName() + " -> " + t.getMessage());
                t.printStackTrace();
            }
        }
    }
}
