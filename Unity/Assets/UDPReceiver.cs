using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Globalization;

public class UDPReceiver : MonoBehaviour
{
    UdpClient udp;
    Thread thread;
    string received = "0,0,0,0,1";

    float baseRotationX = 0f;
    float baseRotationY = 0f;

    bool wasRotating = false;

    public float rotateSensitivity = 0.1f;

    void Start()
    {
        CreateColoredCube();

        udp = new UdpClient(5005);
        thread = new Thread(ReceiveData);
        thread.IsBackground = true;
        thread.Start();

        Debug.Log("UDP Receiver Started");
    }

    void ReceiveData()
    {
        while (true)
        {
            IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
            byte[] data = udp.Receive(ref anyIP);
            received = Encoding.UTF8.GetString(data).Trim();
        }
    }

    void Update()
    {
        string[] values = received.Split(',');
        if (values.Length < 5) return;

        int moveSelect = int.Parse(values[0]);
        int rotateMode = int.Parse(values[1]);

        float rotateDx = float.Parse(values[2], CultureInfo.InvariantCulture);
        float rotateDy = float.Parse(values[3], CultureInfo.InvariantCulture);
        float scale = float.Parse(values[4], CultureInfo.InvariantCulture);

        if (rotateMode == 1)
        {
            if (!wasRotating)
            {
                baseRotationX = transform.eulerAngles.x;
                baseRotationY = transform.eulerAngles.y;
                wasRotating = true;
            }

            float newY = baseRotationY + rotateDx * rotateSensitivity;

            // 上下を逆に変更
            float newX = baseRotationX + rotateDy * rotateSensitivity;

            transform.rotation = Quaternion.Euler(newX, newY, 0);
        }
        else
        {
            wasRotating = false;
        }

        transform.localScale = Vector3.one * scale;
    }

    void CreateColoredCube()
    {
        Mesh mesh = GetComponent<MeshFilter>().mesh;

        Color[] colors = new Color[mesh.vertices.Length];

        for (int i = 0; i < colors.Length; i++)
        {
            Vector3 normal = mesh.normals[i];

            if (normal == Vector3.up)
                colors[i] = Color.red;
            else if (normal == Vector3.down)
                colors[i] = Color.blue;
            else if (normal == Vector3.left)
                colors[i] = Color.green;
            else if (normal == Vector3.right)
                colors[i] = Color.yellow;
            else if (normal == Vector3.forward)
                colors[i] = Color.magenta;
            else
                colors[i] = Color.cyan;
        }

        mesh.colors = colors;

        Material mat = new Material(Shader.Find("Sprites/Default"));
        GetComponent<Renderer>().material = mat;
    }

    void OnApplicationQuit()
    {
        if (thread != null) thread.Abort();
        if (udp != null) udp.Close();
    }
}