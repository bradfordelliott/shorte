/* cairo access */
%module cairo_access
%{

#if defined HAS_CAIRO
    #include "cairo.h"
#else
    #define CAIRO_FORMAT_ARGB24 1
    #define CAIRO_FORMAT_ARGB32 0 
    #define CAIRO_FORMAT_RGB24 2
    #define CAIRO_FORMAT_A8 3
    #define CAIRO_FORMAT_A1 4

    typedef struct cairo_s
    {
        int blah;
    }cairo_t;

    typedef struct cairo_surface_s
    {
        int blah;
    }cairo_surface_t;

    typedef enum _cairo_antialias
    {
    CAIRO_ANTIALIAS_DEFAULT=0,
    CAIRO_ANTIALIAS_NONE=1,
    CAIRO_ANTIALIAS_GRAY=2,
    CAIRO_ANTIALIAS_SUBPIXEL=3
    } cairo_antialias_t;
     
    typedef struct cairo_text_extents_s
    {
        int width;
        int height;
    }cairo_text_extents_t;

    cairo_surface_t* cairo_image_surface_create(int, int, int)
    {
        cairo_surface_t* surface = new cairo_surface_t;

        return surface;
    }

    cairo_t* cairo_create(cairo_surface_t* surface)
    {
        cairo_t* cairo = new cairo_t;
        return cairo;
    }
    
    void cairo_set_source_rgb(cairo_t* c, int r, int g, int b)
    {
    }

    void cairo_rectangle(cairo_t* c, int a, int b, int w, int h){}
    void cairo_fill(cairo_t* c){}
    int cairo_image_surface_get_height(cairo_surface_t* s){return 0;}
    int cairo_image_surface_get_width(cairo_surface_t* s){return 0;}
    unsigned char* cairo_image_surface_get_data(cairo_surface_t* s){return NULL;}
    void cairo_surface_flush(cairo_surface_t* s){}
    void cairo_surface_write_to_png(cairo_surface_t* s, const char* file){}
    void cairo_stroke(cairo_t* c){}
    void cairo_stroke_preserve(cairo_t* c){}
    void cairo_save(cairo_t* c){}
    void cairo_restore(cairo_t* c){}
    void cairo_scale(cairo_t* c, double width, double height){}
    void cairo_translate(cairo_t* c, double x, double y){}
    void cairo_rotate(cairo_t* c, double angle){}
    void cairo_arc(cairo_t* c, double xc, double yc, double radius, double angle1, double angle2){}
    void cairo_fill_preserve(cairo_t* c){}
    void cairo_show_text(cairo_t* c, const char* t){}
    void cairo_set_font_size(cairo_t* c, double size){}
    void cairo_text_extents(cairo_t* c, const char* utf8, cairo_text_extents_t* ext){}
    void cairo_line_to(cairo_t* c, double x, double y){}
    void cairo_set_line_width(cairo_t* c, double w){}
    void cairo_set_dash(cairo_t* c, double dashes[], int num, double offset){}
    void cairo_move_to(cairo_t* c, double x, double y){}
    void cairo_curve_to(cairo_t* c, double x1, double y1, double x2, double y2, double x3, double y3){}
    void cairo_rel_curve_to(cairo_t* c, double x1, double y1, double x2, double y2, double x3, double y3){}
    void cairo_new_path(cairo_t* c){}
    void cairo_close_path(cairo_t* c){}
    void cairo_set_antialias(cairo_t* c, cairo_antialias_t f){}
    void cairo_select_font_face(cairo_t *cr,
                                const char *family,
                                cairo_font_slant_t slant,
                                cairo_font_weight_t weight){}
    

#endif // HAS_CAIRO

    #define min(a,b) (((a)<(b))?(a):(b))
    
    class cairo{
    public:
        cairo(int width, int height)
        {
            m_cairo_surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, width, height);
            m_cairo_image   = cairo_create(m_cairo_surface);

            // Create with a transparent background
            cairo_set_source_rgba(m_cairo_image, 1, 1, 1, 0);
            cairo_rectangle(m_cairo_image, 0, 0, width, height);
            cairo_fill(m_cairo_image);
        }
        
        void rectangle(double x, double y, double width, double height)
        {
            cairo_rectangle(m_cairo_image, x, y, width, height);
        }
        
        void ellipse(double x, double y, double width, double height)
        {
        }
        
        void write_to_png(const char* file, int width_destination, int height_destination)
        {
            int            width_source;
            int            height_source;
            unsigned char* data_source;
            unsigned char* data_destination;
            int            row;
            cairo_status_t status;
    
            cairo_surface_t* new_surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, width_destination, height_destination);
            
            // Set the height/width of the surfaces
            height_source = cairo_image_surface_get_height(m_cairo_surface);
            width_source = cairo_image_surface_get_width(m_cairo_surface);
            
            // Get a pointer to the data of the original image surface
            data_source = cairo_image_surface_get_data(m_cairo_surface);
            data_destination = cairo_image_surface_get_data(new_surface);
            
            for(row = 0; row < min(height_source, height_destination); row++)
            {
                // If the source is wider than the destination surface then
                // only copy the source width amount for each row.
                if(width_source > width_destination)
                {
                    memcpy(data_destination + (row * width_destination * 4),
                           data_source + (row * width_source * 4), width_destination * 4);
                }
                else
                {
                    memcpy(data_destination + (row * width_destination * 4),
                           data_source + (row * width_source * 4), width_source * 4);
                }
            }
            
            // Flush the output surface since we've modified it
            cairo_surface_flush(new_surface);
            status = cairo_surface_write_to_png(new_surface, file);
        }
        
        void set_source_rgb(double red, double green, double blue)
        {
            cairo_set_source_rgb(m_cairo_image, red, green, blue);
        }
        
        void stroke(void)
        {
            cairo_stroke(m_cairo_image);
        }
        void stroke_preserve(void)
        {
            cairo_stroke_preserve(m_cairo_image);
        }
        
        void fill(void)
        {
            cairo_fill(m_cairo_image);
        }
        
        void save(void)
        {
            cairo_save(m_cairo_image);
        }
        
        void restore(void)
        {
            cairo_restore(m_cairo_image);
        }
        
        void scale(double width, double height)
        {
            cairo_scale(m_cairo_image, width, height);
        }
        
        void translate(double x, double y)
        {
            cairo_translate(m_cairo_image, x, y);
        }
        
        void rotate(double angle)
        {
            cairo_rotate(m_cairo_image, angle);
        }
        
        void arc(double xc, double yc, double radius, double angle1, double angle2)
        {
            cairo_arc(m_cairo_image, xc, yc, radius, angle1, angle2);
        }
        
        void fill_preserve(void)
        {
            cairo_fill_preserve(m_cairo_image);
        }
        
        void show_text(const char* text)
        {
            cairo_show_text(m_cairo_image, text);
        }
        
        void set_font_size(double size)
        {
            cairo_set_font_size(m_cairo_image, size);
        }
        
        void text_extents(const char *utf8,
                          int*        width,
                          int*        height)
        {
            cairo_text_extents_t extents;
            cairo_text_extents(m_cairo_image, utf8, &extents);
            
            *width = extents.width;
            *height = extents.height;
        }

        void select_font_face(
            const char*         family,
            cairo_font_slant_t  slant,
            cairo_font_weight_t weight)
        {
            cairo_select_font_face(m_cairo_image, family, slant, weight);
        }
                                             
        void line_to(double x, double y)
        {
            cairo_line_to(m_cairo_image, x, y);
        }

        void rel_line_to(double x, double y)
        {
            cairo_rel_line_to(m_cairo_image, x, y);
        }
        
        void set_line_width(double width)
        {
            cairo_set_line_width(m_cairo_image, width);
        }
        
        double set_dash(double input_dashes[], int num_dashes, double offset)
        {
            cairo_set_dash(m_cairo_image, input_dashes, num_dashes, offset);
            
            return input_dashes[1];
        }
        
        void move_to(double x, double y)
        {
            cairo_move_to(m_cairo_image, x, y);
        }
        
        void curve_to(double x1, double y1, double x2,
                      double y2, double x3, double y3)
        {
            cairo_curve_to(m_cairo_image, x1, y1, x2, y2, x3, y3);
        }
        void rel_curve_to(double x1, double y1, double x2,
                      double y2, double x3, double y3)
        {
            cairo_rel_curve_to(m_cairo_image, x1, y1, x2, y2, x3, y3);
        }
        
        void new_path(void)
        {
            cairo_new_path(m_cairo_image);
        }
        
        void close_path(void)
        {
            cairo_close_path(m_cairo_image);
        }
        
        void set_antialias(cairo_antialias_t format)
        {
            cairo_set_antialias(m_cairo_image, format);
        }

        void destroy(void)
        {
            cairo_surface_destroy(m_cairo_surface);
            cairo_destroy(m_cairo_image);
        }
        
    private:
        cairo_t*         m_cairo_image;
        cairo_surface_t* m_cairo_surface;
    };
%}

#if defined(HAS_CAIRO)
#include "cairo.h"
#endif // HAS_CAIRO

%include "typemaps.i"
%include "carrays.i"

%array_functions(double, doubleArray);

%apply int *OUTPUT { int *width };
%apply int *OUTPUT { int *height };
//%apply double *INPUT { double* input_dashes };


%typedef enum _cairo_format {
    CAIRO_FORMAT_ARGB32,
    CAIRO_FORMAT_RGB24,
    CAIRO_FORMAT_A8,
    CAIRO_FORMAT_A1,
} cairo_format_t;


%typedef enum _cairo_antialias
{
    CAIRO_ANTIALIAS_DEFAULT,
    CAIRO_ANTIALIAS_NONE,
    CAIRO_ANTIALIAS_GRAY,
    CAIRO_ANTIALIAS_SUBPIXEL
} cairo_antialias_t;

%typedef enum {
    CAIRO_FONT_SLANT_NORMAL,
    CAIRO_FONT_SLANT_ITALIC,
    CAIRO_FONT_SLANT_OBLIQUE
} cairo_font_slant_t;

%typedef enum {
    CAIRO_FONT_WEIGHT_NORMAL,
    CAIRO_FONT_WEIGHT_BOLD
} cairo_font_weight_t;

#define min(a,b) (((a)<(b))?(a):(b))

class cairo{
    public:
        cairo(int width, int height)
        {
            m_cairo_surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, width, height);
            m_cairo_image = cairo_create(m_cairo_surface);
        }
        
        void rectangle(double x, double y, double width, double height)
        {
            cairo_rectangle(m_cairo_image, x, y, width, height);
        }
        
        void ellipse(double x, double y, double width, double height)
        {
            cairo_save(m_cairo_image);
            
            cairo_translate(m_cairo_image, x + width / 2., y + height / 2.);
            cairo_scale(m_cairo_image, 1. * (width / 2.), 1. * (height / 2.));
            cairo_arc(m_cairo_image, 0., 0., 1., 0., 2 * 3.1457);
            
            //self.SetupFill()
            //ctx.fill_preserve()
            //self.SetupStroke()
            //ctx.stroke()
            
            //ctx.restore();
        }
        
        void write_to_png(const char* file, int width_destination, int height_destination)
        {
            int            width_source;
            int            height_source;
            unsigned char* data_source;
            unsigned char* data_destination;
            int            row;
            cairo_status_t status;
    
            cairo_surface_t* new_surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, width_destination, height_destination);
            
            // Set the height/width of the surfaces
            height_source = cairo_image_surface_get_height(m_cairo_surface);
            width_source = cairo_image_surface_get_width(m_cairo_surface);
            
            // Get a pointer to the data of the original image surface
            data_source = cairo_image_surface_get_data(m_cairo_surface);
            data_destination = cairo_image_surface_get_data(new_surface);
            
            for(row = 0; row < min(height_source, height_destination); row++)
            {
                // If the source is wider than the destination surface then
                // only copy the source width amount for each row.
                if(width_source > width_destination)
                {
                    memcpy(data_destination + (row * width_destination * 4),
                           data_source + (row * width_source * 4), width_destination * 4);
                }
                else
                {
                    memcpy(data_destination + (row * width_destination * 4),
                           data_source + (row * width_source * 4), width_source * 4);
                }
            }
            
            // Flush the output surface since we've modified it
            cairo_surface_flush(new_surface);
            status = cairo_surface_write_to_png(new_surface, file);
        }
        
        void set_source_rgb(double red, double green, double blue)
        {
            cairo_set_source_rgb(m_cairo_image, red, green, blue);
        }
        
        void stroke(void)
        {
            cairo_stroke(m_cairo_image);
        }
        void stroke_preserve(void)
        {
            cairo_stroke_preserve(m_cairo_image);
        }
        
        void fill(void)
        {
            cairo_fill(m_cairo_image);
        }
        
        void save(void)
        {
            cairo_save(m_cairo_image);
        }
        
        void restore(void)
        {
            cairo_restore(m_cairo_image);
        }
        
        void scale(double width, double height)
        {
            cairo_scale(m_cairo_image, width, height);
        }
        
        void translate(double x, double y)
        {
            cairo_translate(m_cairo_image, x, y);
        }
        
        void arc(double xc, double yc, double radius, double angle1, double angle2)
        {
            cairo_arc(m_cairo_image, xc, yc, radius, angle1, angle2);
        }
        
        void rotate(double angle)
        {
            cairo_rotate(m_cairo_image, angle);
        }
        
        void fill_preserve(void)
        {
            cairo_fill_preserve(m_cairo_image);
        }
            
        void show_text(const char* text)
        {
            cairo_show_text(m_cairo_image, text);
        }
        
        void set_font_size(double size)
        {
            cairo_set_font_size(m_cairo_image, size);
        }
        
        void text_extents(const char *utf8,
                          int*        width,
                          int*        height)
        {
            cairo_text_extents_t extents;
            cairo_text_extents(m_cairo_image, utf8, &extents);
            
            *width = extents.width;
            *height = extents.height;
        }
        
        void select_font_face(
            const char*         family,
            cairo_font_slant_t  slant,
            cairo_font_weight_t weight)
        {
            cairo_select_font_face(m_cairo_image, family, slant, weight);
        }
        
        void line_to(double x, double y)
        {
            cairo_line_to(m_cairo_image, x, y);
        }
        void rel_line_to(double x, double y)
        {
            cairo_rel_line_to(m_cairo_image, x, y);
        }
        
        void set_line_width(double width)
        {
            cairo_set_line_width(m_cairo_image, width);
        }
        
        double set_dash(double input_dashes[], int num_dashes, double offset)
        {
            cairo_set_dash(m_cairo_image, input_dashes, num_dashes, offset);
            
            return input_dashes[1];
        }
        
        void move_to(double x, double y)
        {
            cairo_move_to(m_cairo_image, x, y);
        }
        
        void curve_to(double x1, double y1, double x2,
                      double y2, double x3, double y3)
        {
            cairo_curve_to(m_cairo_image, x1, y1, x2, y2, x3, y3);
        }
        void rel_curve_to(double x1, double y1, double x2,
                      double y2, double x3, double y3)
        {
            cairo_rel_curve_to(m_cairo_image, x1, y1, x2, y2, x3, y3);
        }
        
        void new_path(void)
        {
            cairo_new_path(m_cairo_image);
        }
        
        void close_path(void)
        {
            cairo_close_path(m_cairo_image);
        }
        
        void set_antialias(cairo_antialias_t format);
        
        void destroy(void);
    
    private:
        cairo_t*         m_cairo_image;
        cairo_surface_t* m_cairo_surface;
};
